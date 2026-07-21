from etf_option_analyzer.models.market import OptionChain, OptionType, OptionContract


def pick_candidates(chain: OptionChain, direction: str) -> dict:
    main_type = OptionType.CALL if direction == "long" else OptionType.PUT
    hedge_type = OptionType.PUT if direction == "long" else OptionType.CALL
    main_pool = chain.calls if main_type is OptionType.CALL else chain.puts
    hedge_pool = chain.puts if hedge_type is OptionType.PUT else chain.calls
    mains = sorted(main_pool, key=lambda o: (abs(abs(o.delta)-.65), -o.volume))[:3]
    hedges = sorted(hedge_pool, key=lambda o: (abs(abs(o.delta)-.32), -o.volume))[:3]
    return {"main": mains, "hedge": hedges}


def build_portfolios(main: list[OptionContract], hedge: list[OptionContract]) -> list[dict]:
    profiles = ["保守型", "均衡型", "进攻型"]
    combos = []
    for name, m, h in zip(profiles, main, hedge):
        cost = m.ask + h.ask
        close_value = m.bid + h.bid
        combos.append({
            "profile": name, "main": m, "hedge": h, "conservative_cost": cost, "close_value": close_value,
            "spread_cost": cost - close_value, "max_loss": cost, "net_delta": m.delta + h.delta,
            "gamma": m.gamma + h.gamma, "theta": m.theta + h.theta, "vega": m.vega + h.vega,
            "liquidity_score": 80, "vol_score": 70, "score": 75,
        })
    return combos
