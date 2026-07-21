from etf_option_analyzer.models.market import MarketSnapshot

CRITICAL_CONTRACT_FIELDS = ("code", "strike", "expiry", "dte", "bid", "ask", "iv", "delta")


def validate_snapshot(snapshot: MarketSnapshot) -> dict:
    issues = []
    if len(snapshot.history) < 120:
        issues.append("历史OHLCV少于120个交易日")
    if len(snapshot.expiries) < 2:
        issues.append("有效到期月份少于2个")
    if snapshot.underlying.meta.stale or not snapshot.underlying.meta.complete:
        issues.append("标的行情过期或字段不完整")
    for chain in snapshot.chains:
        if chain.meta.stale or not chain.meta.complete:
            issues.append(f"{chain.expiry}期权链过期或字段不完整")
        for option in chain.calls + chain.puts:
            missing = [f for f in CRITICAL_CONTRACT_FIELDS if getattr(option, f, None) in (None, "")]
            if missing:
                issues.append(f"{option.code}关键字段缺失: {','.join(missing)}")
    issues.extend(snapshot.conflicts)
    return {"ok": not issues, "issues": issues, "signal_allowed": not issues}
