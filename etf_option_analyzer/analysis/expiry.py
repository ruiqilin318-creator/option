from datetime import date


def select_front_next(expiries: list[date]) -> tuple[date, date]:
    valid = sorted(set(expiries))
    if len(valid) < 2:
        raise ValueError("at least two effective expiries are required")
    return valid[0], valid[1]


def expiry_warnings(front: date, today: date) -> list[str]:
    dte = (front - today).days
    warnings = []
    if dte < 10:
        warnings.append("当月DTE低于10天，Theta和Gamma风险显著。")
    if dte < 5:
        warnings.append("当月DTE低于5天，不作为默认3～5日主腿。")
    return warnings
