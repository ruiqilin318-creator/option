# OPTION Project

ETF/指数期权买方保险组合自动分析系统（不自动下单）。当前版本完成项目骨架、Provider接口、标准数据模型、到期月份选择、期权链标准化、数据质量校验、模拟数据源、Markdown示例报告与单元测试。

## 支持标的

- 510050
- 510300
- 510500
- 159915
- 588000

## Provider架构

系统通过 `MarketDataProvider` 适配器统一接入行情源，标准输出 `MarketSnapshot`：

- `MockProvider`：可运行的模拟主数据源，用于开发、测试与示例报告。
- `EastMoneyProvider`：东方财富适配器占位，后续封装HTTP抓取与字段映射。
- `TongHuaShunProvider`：同花顺适配器占位，用于多源交叉验证。
- `TencentSinaProvider`：腾讯/新浪财经备用源适配器占位。
- `CsvOfflineProvider`：CSV离线Provider入口，用于回放与断网分析。
- `SnapshotCache`：历史快照缓存，记录数据源、抓取时间和标准化内容。

## 快速运行

```bash
python -m etf_option_analyzer > examples/sample_report.md
pytest -q
```

## 数据质量原则

当关键字段缺失、行情过期或多数据源冲突时，系统只输出数据质量报告，不输出具体交易信号。
