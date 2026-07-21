from __future__ import annotations

import argparse
from datetime import date

import pytz
from apscheduler.schedulers.blocking import BlockingScheduler

from .analyzer import analyze_snapshot
from .config import default_config
from .data import AkShareDataProvider
from .pdf import write_pdf


def run_once(symbol_code: str | None = None) -> list[str]:
    config = default_config()
    provider = AkShareDataProvider(config)
    reports: list[str] = []
    symbols = [s for s in config.symbols if symbol_code in (None, s.code, s.name)]
    for symbol in symbols:
        snapshot = provider.fetch_snapshot(symbol)
        report = analyze_snapshot(snapshot, config)
        reports.append(str(write_pdf(report, config.output_dir)))
    return reports


def schedule() -> None:
    config = default_config()
    provider = AkShareDataProvider(config)
    scheduler = BlockingScheduler(timezone=pytz.timezone(config.timezone))

    def job() -> None:
        if not provider.is_trading_day(date.today()):
            print("非交易日，跳过自动报告。")
            return
        for path in run_once():
            print(f"已生成：{path}")

    for item in config.schedule_times:
        hour, minute = item.split(":")
        scheduler.add_job(job, "cron", hour=int(hour), minute=int(minute), id=f"report_{hour}{minute}")
    print("自动报告调度已启动：" + ", ".join(config.schedule_times))
    scheduler.start()


def main() -> None:
    parser = argparse.ArgumentParser(description="ETF期权自动抓取与PDF报告")
    sub = parser.add_subparsers(dest="command")
    once = sub.add_parser("run-once", help="立即抓取并生成PDF")
    once.add_argument("--symbol", help="标的代码或名称，例如510300、588000")
    sub.add_parser("schedule", help="按交易日固定时间自动生成PDF")
    args = parser.parse_args()
    if args.command == "schedule":
        schedule()
    else:
        for path in run_once(getattr(args, "symbol", None)):
            print(path)


if __name__ == "__main__":
    main()
