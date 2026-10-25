from __future__ import annotations

from datetime import datetime, timedelta, timezone
import aiomysql
from aiomysql.cursors import DictCursor

from app.market.models import MarketSnapshot, OptionSide


class SnapshotStore:
    def __init__(
        self,
        *,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
    ) -> None:
        self.connection_settings = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "db": database,
            "charset": "utf8mb4",
            "autocommit": False,
        }
        self.pool: aiomysql.Pool | None = None

    async def initialize(self) -> None:
        if not self.connection_settings["password"]:
            raise ValueError("Set DB_PASSWORD in your local .env file.")

        self.pool = await aiomysql.create_pool(
            **self.connection_settings,
            minsize=1,
            maxsize=5,
        )

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS option_snapshots (
                        index_code VARCHAR(20) NOT NULL,
                        expiry DATE NOT NULL,
                        strike INT NOT NULL,
                        side VARCHAR(2) NOT NULL,
                        snapshot_at DATETIME(6) NOT NULL,
                        open_interest BIGINT NOT NULL,
                        previous_close_oi BIGINT NOT NULL,
                        last_price DECIMAL(14, 4) NOT NULL,
                        volume BIGINT NOT NULL,
                        implied_volatility DECIMAL(10, 4) NOT NULL,
                        PRIMARY KEY (
                            index_code, expiry, strike, side, snapshot_at
                        ),
                        INDEX idx_snapshot_lookup (
                            index_code, expiry, strike, side, snapshot_at
                        )
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
            await conn.commit()

    async def close(self) -> None:
        if self.pool is not None:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None

    async def save(self, snapshot: MarketSnapshot) -> None:
        if self.pool is None:
            raise RuntimeError("Call initialize() before saving snapshots.")

        timestamp_utc = snapshot.timestamp.astimezone(
            timezone.utc
        ).replace(tzinfo=None)

        rows = [
            (
                snapshot.index_code,
                snapshot.expiry,
                quote.strike,
                quote.side.value,
                timestamp_utc,
                quote.open_interest,
                quote.previous_close_oi,
                quote.last_price,
                quote.volume,
                quote.implied_volatility,
            )
            for quote in snapshot.options
        ]

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.executemany("""
                    INSERT IGNORE INTO option_snapshots (
                        index_code, expiry, strike, side, snapshot_at,
                        open_interest, previous_close_oi, last_price,
                        volume, implied_volatility
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, rows)
            await conn.commit()

    async def rolling_oi_change(
        self,
        index_code: str,
        expiry: str,
        strike: int,
        side: OptionSide,
        window_minutes: int,
    ) -> dict | None:
        if self.pool is None:
            raise RuntimeError("Call initialize() before reading snapshots.")
        if window_minutes <= 0:
            raise ValueError("window_minutes must be positive.")

        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cursor:
                await cursor.execute("""
                    SELECT snapshot_at, open_interest
                    FROM option_snapshots
                    WHERE index_code=%s AND expiry=%s
                      AND strike=%s AND side=%s
                    ORDER BY snapshot_at DESC
                    LIMIT 1
                """, (index_code, expiry, strike, side.value))
                current = await cursor.fetchone()

                if current is None:
                    return None

                cutoff = current["snapshot_at"] - timedelta(
                    minutes=window_minutes
                )

                await cursor.execute("""
                    SELECT snapshot_at, open_interest
                    FROM option_snapshots
                    WHERE index_code=%s AND expiry=%s
                      AND strike=%s AND side=%s
                      AND snapshot_at <= %s
                    ORDER BY snapshot_at DESC
                    LIMIT 1
                """, (index_code, expiry, strike, side.value, cutoff))
                baseline = await cursor.fetchone()

        if baseline is None:
            return None

        current_oi = int(current["open_interest"])
        baseline_oi = int(baseline["open_interest"])
        difference = current_oi - baseline_oi

        return {
            "current_oi": current_oi,
            "baseline_oi": baseline_oi,
            "change": difference,
            "change_percent": (
                difference / baseline_oi * 100 if baseline_oi else None
            ),
            "current_timestamp": current["snapshot_at"].replace(
                tzinfo=timezone.utc
            ),
            "baseline_timestamp": baseline["snapshot_at"].replace(
                tzinfo=timezone.utc
            ),
        }