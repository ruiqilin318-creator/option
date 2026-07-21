from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .analyzer import AnalysisReport


def write_pdf(report: AnalysisReport, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = report.snapshot.timestamp.strftime("%Y%m%d_%H%M")
    path = output_dir / f"{ts}_{report.snapshot.symbol.code}_{report.snapshot.symbol.name}_option_report.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"{report.snapshot.symbol.name} 自动期权分析报告", styles["Title"]),
        Paragraph(f"生成时间：{report.snapshot.timestamp:%Y-%m-%d %H:%M:%S}", styles["Normal"]),
        Paragraph(f"标的价格：{report.snapshot.etf_price}；日涨跌幅：{report.snapshot.etf_daily_change_pct}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("一、波动率判断", styles["Heading2"]),
        Paragraph(report.volatility_comment, styles["Normal"]),
        Spacer(1, 8),
        Paragraph("二、策略结论", styles["Heading2"]),
        Paragraph(report.strategy_comment, styles["Normal"]),
    ]
    if not report.candidates.empty:
        story += [Spacer(1, 8), Paragraph("三、候选组合", styles["Heading2"]), _df_table(report.candidates.drop(columns=["score"], errors="ignore"))]
    if not report.scenarios.empty:
        story += [Spacer(1, 8), Paragraph("四、涨跌情景测算", styles["Heading2"]), _df_table(report.scenarios)]
    story += [Spacer(1, 8), Paragraph("五、固定风控", styles["Heading2"]), Paragraph("只做买方；方向策略默认配置保险腿；不加仓摊低成本；结合Theta、Vega和波动率均线判断是否继续持有。", styles["Normal"])]
    doc.build(story)
    return path


def _df_table(df):
    data = [list(df.columns)] + df.astype(str).values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    return table
