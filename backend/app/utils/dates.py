from datetime import datetime, timedelta


def to_date_str(date: str) -> str:
    if date == "auto":
        today = datetime.now()
        if today.weekday() == 0:
            candidate = today - timedelta(days=3)
        elif today.weekday() == 6:
            candidate = today - timedelta(days=2)
        else:
            candidate = today - timedelta(days=1)
        return candidate.strftime("%Y%m%d")
    if "-" in date:
        return date.replace("-", "")
    return date


def default_start_date(end_date: str, days: int = 260) -> str:
    end = datetime.strptime(to_date_str(end_date), "%Y%m%d")
    start = end - timedelta(days=days * 1.5)
    return start.strftime("%Y%m%d")
