from datetime import date

from etf_option_analyzer.analysis.expiry import select_front_next, expiry_warnings
from etf_option_analyzer.analysis.normalize import normalize_chain
from etf_option_analyzer.analysis.quality import validate_snapshot
from etf_option_analyzer.providers.mock import MockProvider
from etf_option_analyzer.reporting.markdown import render_report


def test_select_front_next_sorts_by_real_expiry():
    front, nxt = select_front_next([date(2026, 9, 23), date(2026, 7, 22), date(2026, 8, 26)])
    assert front == date(2026, 7, 22)
    assert nxt == date(2026, 8, 26)


def test_expiry_warnings_for_near_expiry():
    warnings = expiry_warnings(date(2026, 7, 22), date(2026, 7, 21))
    assert any("Theta" in w for w in warnings)
    assert any("不作为默认" in w for w in warnings)


def test_mock_snapshot_quality_and_chain_normalization():
    snapshot = MockProvider().fetch_snapshot("510050")
    assert validate_snapshot(snapshot)["ok"] is True
    chain = normalize_chain(snapshot.chains[0])
    assert [o.strike for o in chain.calls] == sorted(o.strike for o in chain.calls)
    assert all(o.estimated for o in chain.calls + chain.puts)


def test_report_contains_required_sections():
    report = render_report(MockProvider().fetch_snapshot("510300"), "short")
    assert "数据源及数据时间" in report
    assert "IV压力测试" in report
    assert "风险等级" in report
