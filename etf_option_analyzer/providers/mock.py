from __future__ import annotations

from datetime import date, datetime, timedelta
import math

from etf_option_analyzer.models.market import *
from etf_option_analyzer.models.provider import MarketDataProvider


class MockProvider(MarketDataProvider):
    name = "mock"

    def fetch_snapshot(self, symbol: str) -> MarketSnapshot:
        if symbol not in SUPPORTED_UNDERLYINGS:
            raise ValueError(f"unsupported underlying: {symbol}")
        now = datetime(2026, 7, 21, 10, 30)
        meta = QuoteMeta(self.name, now, now - timedelta(seconds=3), 3, False, True)
        spot = {"510050": 2.65, "510300": 4.05, "510500": 6.2, "159915": 2.1, "588000": 1.25}[symbol]
        underlying = UnderlyingQuote(symbol, spot, spot * .992, spot * .995, spot * 1.012, spot * .987, .81, 123456789, 321000000, meta)
        history = _history(spot)
        expiries = [date(2026, 7, 22), date(2026, 8, 26), date(2026, 9, 23), date(2026, 12, 23)]
        chains = [_chain(symbol, spot, exp, now, meta) for exp in expiries[:2]]
        return MarketSnapshot(underlying, history, expiries, chains, self.name, now)


def _history(spot: float) -> list[OHLCV]:
    start = date(2026, 1, 26)
    rows = []
    for i in range(130):
        close = spot * (0.92 + i * 0.0007 + math.sin(i / 7) * 0.025)
        rows.append(OHLCV(start + timedelta(days=i), close * .995, close * 1.01, close * .99, close, 1000000 + i * 1000, close * 1000000))
    return rows


def _chain(symbol: str, spot: float, expiry: date, now: datetime, meta: QuoteMeta) -> OptionChain:
    dte = max((expiry - now.date()).days, 0)
    strikes = [round(spot * m, 3) for m in (.9, .95, 1.0, 1.05, 1.1)]
    calls, puts = [], []
    for strike in strikes:
        for typ in (OptionType.CALL, OptionType.PUT):
            intrinsic = max(spot - strike, 0) if typ is OptionType.CALL else max(strike - spot, 0)
            mny = abs(math.log(spot / strike))
            tv = max(0.015, spot * (0.035 + dte / 365 * 0.08 - mny * .03))
            last = intrinsic + tv
            delta = (0.65 if strike <= spot else 0.35) if typ is OptionType.CALL else (-0.65 if strike >= spot else -0.35)
            option = OptionContract(
                code=f"MOCK{symbol}{expiry:%y%m%d}{typ.value[0].upper()}{int(strike*1000)}",
                name=f"{symbol}{expiry:%Y%m%d}{'购' if typ is OptionType.CALL else '沽'}{strike}",
                option_type=typ, strike=strike, expiry=expiry, dte=dte, last=round(last,4), bid=round(last*.98,4), ask=round(last*1.02,4),
                bid_volume=100, ask_volume=120, previous_close=round(last*.97,4), open=round(last*.99,4), high=round(last*1.08,4), low=round(last*.93,4),
                change_pct=3.1, volume=5000, amount=last*5000000, open_interest=20000, contract_unit=10000, iv=.22+dte/365*.04, delta=delta,
                gamma=.8, theta=-0.01, vega=.12, rho=.01, intrinsic_value=round(intrinsic,4), time_value=round(tv,4), premium_rate=last/spot,
                leverage=spot/last, real_leverage=abs(delta)*spot/last, estimated=True, meta=meta)
            (calls if typ is OptionType.CALL else puts).append(option)
    return OptionChain(symbol, expiry, calls, puts, meta)
