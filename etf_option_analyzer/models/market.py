from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any


SUPPORTED_UNDERLYINGS = {"510050", "510300", "510500", "159915", "588000"}
INSURANCE_DISTANCE = {"510050": 0.03, "510300": 0.03, "510500": 0.04, "159915": 0.04, "588000": 0.05}


class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"


@dataclass(frozen=True)
class QuoteMeta:
    source: str
    fetched_at: datetime
    quote_time: datetime
    delay_seconds: float
    stale: bool
    complete: bool
    missing_fields: list[str] = field(default_factory=list)
    estimated: bool = False


@dataclass(frozen=True)
class UnderlyingQuote:
    symbol: str
    latest: float
    previous_close: float
    open: float
    high: float
    low: float
    change_pct: float
    volume: float
    amount: float
    meta: QuoteMeta


@dataclass(frozen=True)
class OHLCV:
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float


@dataclass(frozen=True)
class OptionContract:
    code: str
    name: str
    option_type: OptionType
    strike: float
    expiry: date
    dte: int
    last: float
    bid: float
    ask: float
    bid_volume: int
    ask_volume: int
    previous_close: float
    open: float
    high: float
    low: float
    change_pct: float
    volume: int
    amount: float
    open_interest: int
    contract_unit: int
    iv: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    intrinsic_value: float
    time_value: float
    premium_rate: float
    leverage: float
    real_leverage: float
    estimated: bool = False
    meta: QuoteMeta | None = None


@dataclass(frozen=True)
class OptionChain:
    symbol: str
    expiry: date
    calls: list[OptionContract]
    puts: list[OptionContract]
    meta: QuoteMeta


@dataclass(frozen=True)
class MarketSnapshot:
    underlying: UnderlyingQuote
    history: list[OHLCV]
    expiries: list[date]
    chains: list[OptionChain]
    provider_name: str
    fetched_at: datetime
    conflicts: list[str] = field(default_factory=list)
    provider_snapshots: dict[str, Any] = field(default_factory=dict)
