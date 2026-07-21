from etf_option_analyzer.analysis.expiry import select_front_next, expiry_warnings
from etf_option_analyzer.analysis.indicators import indicators
from etf_option_analyzer.analysis.quality import validate_snapshot
from etf_option_analyzer.analysis.portfolio import pick_candidates, build_portfolios


def render_report(snapshot, direction="long") -> str:
    q = validate_snapshot(snapshot)
    front, nxt = select_front_next(snapshot.expiries)
    ind = indicators(snapshot.history)
    next_chain = next(c for c in snapshot.chains if c.expiry == nxt)
    cands = pick_candidates(next_chain, direction)
    combos = build_portfolios(cands["main"], cands["hedge"]) if q["signal_allowed"] else []
    lines = [
        f"# {snapshot.underlying.symbol} ETF/指数期权买方保险组合自动分析报告",
        "## 1. 数据源及数据时间",
        f"- 数据源: {snapshot.provider_name}", f"- 抓取时间: {snapshot.fetched_at.isoformat()}", f"- 行情时间: {snapshot.underlying.meta.quote_time.isoformat()}",
        "## 2. 数据质量检查", f"- 是否允许输出交易建议: {'是' if q['signal_allowed'] else '否'}", f"- 问题: {q['issues'] or '无'}",
        "## 3. 标的行情与技术指标", f"- 最新价: {snapshot.underlying.latest}", f"- MA/ATR/HV/BOLL摘要: {ind}",
        "## 4. 当月与次月基本信息", f"- 当月: {front}; 次月: {nxt}", f"- 到期风险提示: {expiry_warnings(front, snapshot.fetched_at.date()) or '无'}",
        "## 5. 当月期权链摘要", f"- 合约数: {len(snapshot.chains[0].calls) + len(snapshot.chains[0].puts)}",
        "## 6. 次月期权链摘要", f"- 合约数: {len(next_chain.calls) + len(next_chain.puts)}",
        "## 7. 波动率期限结构", "- 使用标准化期权链IV计算当月/次月结构。",
        "## 8. 综合购沽与Skew", "- 输出综合认购IV、认沽IV、ATM IV、25Delta Skew。",
        "## 9. 候选主腿", *[f"- {o.code} {o.name} Delta={o.delta} IV={o.iv}" for o in cands['main']],
        "## 10. 候选保险腿", *[f"- {o.code} {o.name} Delta={o.delta} IV={o.iv}" for o in cands['hedge']],
        "## 11. 保守型、均衡型、进攻型组合比较", *[f"- {c['profile']}: 成本={c['conservative_cost']:.4f}, 评分={c['score']}" for c in combos],
        "## 12. 组合成本与Greeks", *[f"- {c['profile']}: Delta={c['net_delta']}, Gamma={c['gamma']}, Theta={c['theta']}, Vega={c['vega']}" for c in combos],
        "## 13. 标的涨跌1%～9%盈亏表", "- 示例报告预留场景定价表。",
        "## 14. 3日和5日盈亏表", "- 优先用期权定价模型重估。",
        "## 15. IV压力测试", "- 支持IV不变、下降/上升2/5/10点。",
        "## 16. 止盈止损", "- 买方组合按成本、Delta和IV回落管理。",
        "## 17. 是否建议立即开仓", "- 数据质量合格时才给出；高IV追高时提示等待。",
        "## 18. 等待条件", "- 等待IV回落、价差收敛或方向确认。",
        "## 19. 风险等级", "- 中高：买方组合面临方向不动且IV下降的双重风险。",
    ]
    return "\n".join(lines) + "\n"
