from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from importlib import import_module
from pathlib import Path

import pandas as pd

from .config import AppConfig, SymbolConfig


@dataclass
class MarketSnapshot:
    symbol: SymbolConfig
    timestamp: datetime
    etf_price: float | None
    etf_daily_change_pct: float | None
    option_chain: pd.DataFrame
    volatility: pd.DataFrame


class AkShareDataProvider:
    """Fetch ETF, option chain, volatility index and China trading-day data."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.ak = import_module("akshare")
        self.config.cache_dir.mkdir(parents=True, exist_ok=True)

    def is_trading_day(self, day: date) -> bool:
        cached = self.config.cache_dir / "trade_dates.csv"
        if cached.exists():
            dates = pd.read_csv(cached)["trade_date"].astype(str).tolist()
        else:
            df = self.ak.tool_trade_date_hist_sina()
            col = "trade_date" if "trade_date" in df.columns else df.columns[0]
            dates = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d").tolist()
            pd.DataFrame({"trade_date": dates}).to_csv(cached, index=False)
        return day.strftime("%Y-%m-%d") in set(dates)

    def fetch_snapshot(self, symbol: SymbolConfig) -> MarketSnapshot:
        now = datetime.now()
        etf_price, etf_change = self._fetch_etf_quote(symbol.code)
        chain = self._fetch_option_chain(symbol)
        vol = self._fetch_volatility_board()
        return MarketSnapshot(symbol, now, etf_price, etf_change, chain, vol)

    def _fetch_etf_quote(self, code: str) -> tuple[float | None, float | None]:
        df = self.ak.fund_etf_spot_em()
        row = df[df.astype(str).apply(lambda s: s.str.contains(code, regex=False)).any(axis=1)]
        if row.empty:
            return None, None
        row0 = row.iloc[0]
        price = _pick_numeric(row0, ["最新价", "最新", "现价"])
        change = _pick_numeric(row0, ["涨跌幅", "涨幅"])
        return price, change

    def _fetch_option_chain(self, symbol: SymbolConfig) -> pd.DataFrame:
        # AkShare exposes several option endpoints and field names vary by version.
        # Keep collection narrow and normalize only the columns used by analysis.
        frames: list[pd.DataFrame] = []
        endpoint_names = (
            "option_finance_board",
            "option_sse_spot_price_sina",
            "option_current_em",
        )
        for name in endpoint_names:
            if hasattr(self.ak, name):
                func = getattr(self.ak, name)
                frame = _call_candidate(func, symbol)
                if isinstance(frame, pd.DataFrame) and not frame.empty:
                    frames.append(frame)
        if not frames:
            return pd.DataFrame()
        raw = pd.concat(frames, ignore_index=True, sort=False).drop_duplicates()
        return normalize_option_chain(raw)

    def _fetch_volatility_board(self) -> pd.DataFrame:
        endpoint_names = ("option_risk_indicator_sse", "option_cffex_hs300_index_sina")
        frames: list[pd.DataFrame] = []
        for name in endpoint_names:
            if hasattr(self.ak, name):
                frame = _call_noarg(getattr(self.ak, name))
                if isinstance(frame, pd.DataFrame) and not frame.empty:
                    frames.append(frame)
        return pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()


def _call_candidate(func, symbol: SymbolConfig):
    for kwargs in ({"symbol": symbol.option_board}, {"symbol": symbol.code}, {}):
        try:
            return func(**kwargs)
        except TypeError:
            continue
        except Exception:
            continue
    return None


def _call_noarg(func):
    try:
        return func()
    except Exception:
        return None


def _pick_numeric(row: pd.Series, names: list[str]) -> float | None:
    for name in names:
        if name in row.index:
            return pd.to_numeric(row[name], errors="coerce")
    return None


def normalize_option_chain(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "合约名称": "contract", "期权名称": "contract", "名称": "contract",
        "最新价": "last", "当前价": "last", "现价": "last",
        "行权价": "strike", "执行价": "strike",
        "到期日": "expiry", "剩余日": "dte",
        "Delta": "delta", "DELTA": "delta",
        "Gamma": "gamma", "GAMMA": "gamma",
        "Theta": "theta", "THETA": "theta",
        "Vega": "vega", "VEGA": "vega",
        "隐含波动率": "iv", "IV": "iv",
        "成交量": "volume", "持仓量": "open_interest",
    }
    out = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}).copy()
    for col in ("last", "strike", "delta", "gamma", "theta", "vega", "iv", "volume", "open_interest"):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    if "contract" in out.columns:
        text = out["contract"].astype(str)
        out["side"] = text.apply(lambda x: "call" if "购" in x or "call" in x.lower() else ("put" if "沽" in x or "put" in x.lower() else ""))
    return out
