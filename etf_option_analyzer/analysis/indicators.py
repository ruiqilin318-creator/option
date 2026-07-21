from statistics import mean, pstdev
from etf_option_analyzer.models.market import OHLCV


def moving_average(values, n):
    return mean(values[-n:]) if len(values) >= n else None


def indicators(history: list[OHLCV]) -> dict:
    closes = [x.close for x in history]
    highs = [x.high for x in history]
    lows = [x.low for x in history]
    vols = [x.volume for x in history]
    returns = [(closes[i]/closes[i-1]-1) for i in range(1, len(closes))]
    out = {f"MA{n}": moving_average(closes, n) for n in (3,5,7,10,17,20,50,60)}
    out.update({f"HV{n}": (pstdev(returns[-n:]) * (252 ** .5) if len(returns) >= n else None) for n in (10,20,30,60)})
    out["VOL_MA10"] = moving_average(vols, 10); out["VOL_MA20"] = moving_average(vols, 20)
    out["support"] = min(lows[-20:]); out["resistance"] = max(highs[-20:])
    mid = out["MA20"]; sd = pstdev(closes[-20:]) if len(closes) >= 20 else 0
    out["BOLL"] = {"mid": mid, "upper": mid + 2*sd if mid else None, "lower": mid - 2*sd if mid else None}
    out["ATR14"] = mean([h-l for h,l in zip(highs[-14:], lows[-14:])]); out["ATR20"] = mean([h-l for h,l in zip(highs[-20:], lows[-20:])])
    out["MACD"] = "placeholder"; out["DMI_ADX"] = "placeholder"; out["CCI"] = "placeholder"
    out["volume_price"] = "量价关系基于成交量均线和价格位置综合判断"
    return out
