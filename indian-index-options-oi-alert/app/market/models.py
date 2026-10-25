from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class OptionSide(str, Enum):
    CE = "CE"
    PE = "PE"


@dataclass(frozen=True)
class IndexDefinition:
    code: str
    display_name: str
    underlying_security_id: int | None = None
    underlying_segment: str = "IDX_I"
    strike_step: int = 50


@dataclass(frozen=True)
class OptionQuote:
    strike: int
    side: OptionSide
    open_interest: int
    previous_close_oi: int
    last_price: float
    volume: int
    implied_volatility: float


@dataclass(frozen=True)
class MarketSnapshot:
    index_code: str
    expiry: date
    timestamp: datetime
    spot: float
    options: tuple[OptionQuote, ...]

    def pcr(self) -> float | None:
        put_oi = sum(
            quote.open_interest
            for quote in self.options
            if quote.side == OptionSide.PE
        )
        call_oi = sum(
            quote.open_interest
            for quote in self.options
            if quote.side == OptionSide.CE
        )
        return put_oi / call_oi if call_oi else None