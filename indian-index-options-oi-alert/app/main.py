import asyncio
import logging

from app.bot.sender import MockAlertSender
from app.market.mock_provider import MockMarketDataProvider
from app.market.registry import get_index
from app.settings import load_settings
from app.storage.snapshots import SnapshotStore


async def run_demo() -> None:
    settings = load_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    provider = MockMarketDataProvider()
    sender = MockAlertSender()

    index = get_index("NIFTY")
    expiries = await provider.get_expiries(index)

    if not expiries:
        raise RuntimeError(f"No mock expiries returned for {index.code}")

    snapshot = await provider.get_snapshot(index, expiries[0])
    store = SnapshotStore(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )
    print("DB host:", repr(settings.db_host), type(settings.db_host))
    print("DB port:", repr(settings.db_port), type(settings.db_port))
    await store.initialize()

    try:
        await store.save(snapshot)
    finally:
        await store.close()


    # pcr = snapshot.pcr()
    # sample_options = snapshot.options[:6]
    #
    # lines = [
    #     f"{index.display_name} market data (MOCK)",
    #     f"Expiry: {snapshot.expiry}",
    #     f"Spot: {snapshot.spot:.2f}",
    #     f"PCR: {pcr:.3f}" if pcr is not None else "PCR: unavailable",
    #     f"Snapshot time: {snapshot.timestamp.isoformat()}",
    #     "",
    #     "Sample options:",
    # ]
    #
    # for quote in sample_options:
    #     lines.append(
    #         f"{quote.strike} {quote.side.value} | "
    #         f"OI {quote.open_interest:,} | "
    #         f"LTP {quote.last_price:.2f} | "
    #         f"Volume {quote.volume:,} | "
    #         f"IV {quote.implied_volatility:.2f}"
    #     )
    #
    # await sender.send_message(chat_id=0, text="\n".join(lines))
    # logger.info("Mock demo completed for %s", index.code)
    #

if __name__ == "__main__":
    asyncio.run(run_demo())
