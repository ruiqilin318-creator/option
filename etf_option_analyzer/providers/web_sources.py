from __future__ import annotations

from etf_option_analyzer.models.provider import MarketDataProvider


class EastMoneyProvider(MarketDataProvider):
    """东方财富Provider占位实现：生产环境在此封装HTTP抓取与字段映射。"""
    name = "eastmoney"
    def fetch_snapshot(self, symbol):
        raise NotImplementedError("EastMoney HTTP adapter not enabled in this scaffold")

class TongHuaShunProvider(MarketDataProvider):
    """同花顺Provider占位实现：用于多源交叉验证。"""
    name = "10jqka"
    def fetch_snapshot(self, symbol):
        raise NotImplementedError("TongHuaShun HTTP adapter not enabled in this scaffold")

class TencentSinaProvider(MarketDataProvider):
    """腾讯/新浪财经Provider占位实现：备用行情源。"""
    name = "tencent_sina"
    def fetch_snapshot(self, symbol):
        raise NotImplementedError("Tencent/Sina HTTP adapter not enabled in this scaffold")
