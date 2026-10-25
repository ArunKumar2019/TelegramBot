from datetime import date
from typing import Protocol

from app.market.models import IndexDefinition, MarketSnapshot


class MarketDataProvider(Protocol):
    async def get_expiries(
        self,
        index: IndexDefinition,
    ) -> list[date]:
        """Return available option expiries for an index."""

    async def get_snapshot(
        self,
        index: IndexDefinition,
        expiry: date,
    ) -> MarketSnapshot:
        """Return the current option-chain snapshot."""