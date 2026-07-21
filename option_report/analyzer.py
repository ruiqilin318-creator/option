from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import AppConfig
from .data import MarketSnapshot


@dataclass
class AnalysisReport:
    snapshot: MarketSnapshot
    volatility_comment: str
    strategy_comment: str
    candidates: pd.DataFrame
    scenarios: pd.DataFrame


def analyze_snapshot(snapshot: MarketSnapshot, config: AppConfig) -> AnalysisReport:
    chain = snapshot.option_chain.copy()
    vol_comment = analyze_volatility(snapshot)
    candidates = select_short_candidates(snapshot, config)
    scenarios = build_scenarios(snapshot, candidates, config)
    if candidates.empty:
        strategy = "期权链数据不足：保留原有逻辑，仅输出波动率与风险提示，暂不臆测组合。"
    else:
        top = candidates.iloc[0]
        strategy = (
            f"首选偏空买方保险组合：买入 {top['put_contract']} + 买入 {top['call_contract']}。"
            f"保险距离约{top['insurance_distance_pct']:.1f}%，净Delta约{top['net_delta']:.2f}。"
        )
    return AnalysisReport(snapshot, vol_comment, strategy, candidates, scenarios)


def analyze_volatility(snapshot: MarketSnapshot) -> str:
    vol = snapshot.volatility
    if vol.empty:
        return "未抓取到综合波动率数据；需结合单腿IV、HV/ATR继续判断。"
    text = " ".join(map(str, vol.tail(20).to_dict("records")))
    key = snapshot.symbol.name.replace("沪深", "300").replace("上证", "50")
    if snapshot.symbol.code in text or key in text:
        return "已抓取综合波动率面板；请重点比较综合、综合购、综合沽与目标单腿IV。"
    return "已抓取综合波动率面板；当前品种未能精确匹配，报告保守引用全市场波动率环境。"


def select_short_candidates(snapshot: MarketSnapshot, config: AppConfig) -> pd.DataFrame:
    chain = snapshot.option_chain
    price = snapshot.etf_price
    if chain.empty or price is None or not {"side", "last", "strike"}.issubset(chain.columns):
        return pd.DataFrame()
    puts = chain[(chain["side"] == "put") & chain["last"].notna() & chain["strike"].notna()].copy()
    calls = chain[(chain["side"] == "call") & chain["last"].notna() & chain["strike"].notna()].copy()
    if puts.empty or calls.empty:
        return pd.DataFrame()
    target = snapshot.symbol.insurance_distance
    rows = []
    for _, p in puts.iterrows():
        for _, c in calls.iterrows():
            if c["strike"] <= price:
                continue
            dist = c["strike"] / price - 1
            if not (target * 0.6 <= dist <= target * 1.8):
                continue
            p_delta = p.get("delta", float("nan"))
            c_delta = c.get("delta", float("nan"))
            net_delta = (0 if pd.isna(p_delta) else p_delta) + (0 if pd.isna(c_delta) else c_delta)
            cost = (p["last"] + c["last"]) * 10000
            score = abs(dist - target) * 100 + max(net_delta + 0.05, 0) * 10 + cost / 100000
            rows.append({
                "put_contract": p.get("contract", f"沽{p['strike']}"),
                "call_contract": c.get("contract", f"购{c['strike']}"),
                "put_price": p["last"], "call_price": c["last"], "cost": cost,
                "put_strike": p["strike"], "call_strike": c["strike"],
                "net_delta": net_delta, "insurance_distance_pct": dist * 100, "score": score,
            })
    return pd.DataFrame(rows).sort_values("score").head(8) if rows else pd.DataFrame()


def build_scenarios(snapshot: MarketSnapshot, candidates: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    if candidates.empty or snapshot.etf_price is None:
        return pd.DataFrame()
    top = candidates.iloc[0]
    rows = []
    cost = top["cost"]
    for pct in list(-s for s in reversed(config.scenario_steps)) + list(config.scenario_steps):
        # Conservative intrinsic-value floor plus current time value proxy.
        s = snapshot.etf_price * (1 + pct / 100)
        put_value = max(top["put_strike"] - s, 0) * 10000
        call_value = max(s - top["call_strike"], 0) * 10000
        intrinsic_floor = put_value + call_value
        approx_value = max(intrinsic_floor, cost + top["net_delta"] * (s - snapshot.etf_price) * 10000)
        pnl = approx_value - cost
        rows.append({"标的涨跌": f"{pct:+d}%", "标的价格": round(s, 4), "估算盈亏": round(pnl, 2), "收益率": f"{pnl / cost:.1%}"})
    return pd.DataFrame(rows)
