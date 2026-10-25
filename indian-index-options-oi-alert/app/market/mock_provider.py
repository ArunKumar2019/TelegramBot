from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.market.models import (
    IndexDefinition,
    MarketSnapshot,
    OptionQuote,
    OptionSide,
)

IST = ZoneInfo("Asia/Kolkata")


class MockMarketDataProvider:
    """Synthetic market data for development without broker credentials."""

    def __init__(self) -> None:
        self._call_count = 0

    async def get_expiries(
        self,
        index: IndexDefinition,
    ) -> list[date]:
        today = datetime.now(IST).date()
        days_until_thursday = (3 - today.weekday()) % 7
        weekly = today.fromordinal(today.toordinal() + days_until_thursday)

        if weekly <= today:
            weekly = today.fromordinal(weekly.toordinal() + 7)

        monthly = weekly
        while (monthly + timedelta(days=7)).month == weekly.month:
            monthly += timedelta(days=7)

        return sorted({weekly, monthly})

    async def get_snapshot(
        self,
        index: IndexDefinition,
        expiry: date,
    ) -> MarketSnapshot:
        self._call_count += 1

        spot = 25_000.0 if index.code == "NIFTY" else 52_000.0
        spot += self._call_count * 2
        atm = round(spot / index.strike_step) * index.strike_step

        options: list[OptionQuote] = []

        for offset in range(-5, 6):
            strike = atm + offset * index.strike_step

            for side in (OptionSide.CE, OptionSide.PE):
                distance = abs(strike - atm)
                options.append(
                    OptionQuote(
                        strike=strike,
                        side=side,
                        open_interest=1_000_000 + offset * 10_000
                        if side == OptionSide.CE
                        else 1_100_000 - offset * 8_000,
                        previous_close_oi=980_000,
                        last_price=max(10.0, 220.0 - distance * 0.8),
                        volume=75_000 + self._call_count * 100,
                        implied_volatility=14.5 + distance / 100,
                    )
                )

        return MarketSnapshot(
            index_code=index.code,
            expiry=expiry,
            timestamp=datetime.now(IST),
            spot=spot,
            options=tuple(options),
        )