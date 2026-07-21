from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SymbolConfig:
    name: str
    code: str
    option_board: str
    insurance_distance: float


@dataclass(frozen=True)
class AppConfig:
    timezone: str = "Asia/Shanghai"
    schedule_times: tuple[str, ...] = ("09:45", "10:45", "11:45", "13:30", "14:40")
    output_dir: Path = Path("reports")
    cache_dir: Path = Path(".cache/option-report")
    holding_days: tuple[int, int] = (3, 5)
    scenario_steps: tuple[int, ...] = tuple(range(1, 10))
    symbols: tuple[SymbolConfig, ...] = field(default_factory=lambda: (
        SymbolConfig("沪深300ETF", "510300", "沪深300ETF期权", 0.03),
        SymbolConfig("上证50ETF", "510050", "上证50ETF期权", 0.03),
        SymbolConfig("中证500ETF", "510500", "中证500ETF期权", 0.03),
        SymbolConfig("创业板ETF", "159915", "创业板ETF期权", 0.04),
        SymbolConfig("科创50ETF", "588000", "科创50ETF期权", 0.05),
    ))


def default_config() -> AppConfig:
    return AppConfig()
