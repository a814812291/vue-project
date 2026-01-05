import json
import logging
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Tuple

from ..providers.default_provider import DefaultDataProvider
from ..utils.dates import to_date_str, default_start_date
from . import cache

logger = logging.getLogger(__name__)


def _load_hot_keywords():
    import os

    path = os.path.join(os.path.dirname(__file__), "..", "hot_money_keywords.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def tag_hot_money(lhb_items: List[Dict]):
    keywords = _load_hot_keywords()
    for it in lhb_items:
        raw = json.dumps(it, ensure_ascii=False)
        hits = [kw for kw in keywords if kw in raw]
        it["hot_keywords"] = hits
    return lhb_items


def normalize_concepts(reason: str) -> List[str]:
    if not reason:
        return []
    parts = reason.replace("；", ";").replace("|", ";").replace("/", ";")
    parts = [p.strip() for p in parts.split(";") if p.strip()]
    normalized = []
    for p in parts:
        if "数字" in p:
            normalized.append("数字经济")
        elif "人工智能" in p or "AI" in p:
            normalized.append("人工智能")
        else:
            normalized.append(p)
    return normalized


def aggregate_themes(items: List[Dict]) -> List[Dict]:
    score = defaultdict(lambda: {"count": 0, "consecutive": 0, "fd": 0, "amount": 0})
    for it in items:
        concepts = normalize_concepts(it.get("reason", ""))
        if not concepts:
            concepts = [it.get("industry", "未知行业")]
        for c in concepts:
            entry = score[c]
            entry["count"] += 1
            entry["consecutive"] += max(int(it.get("consecutive") or 1), 1)
            entry["fd"] += float(it.get("fd_amount") or 0)
            entry["amount"] += float(it.get("amount") or 0)
    ranked = []
    for name, v in score.items():
        weighted = v["count"] * 1.0 + v["consecutive"] * 0.5 + v["fd"] / 1e8 + v["amount"] / 1e9
        ranked.append({"name": name, "score": round(weighted, 2), **v})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[:10]


def compute_sentiment(items: List[Dict], prev_items: List[Dict]) -> Dict:
    if not items:
        return {}
    max_consecutive = max(it.get("consecutive", 1) or 1 for it in items)
    total = len(items)
    open_fail = len([i for i in items if (i.get("open_times") or 0) > 0])
    lianban = len([i for i in items if (i.get("consecutive") or 1) > 1])
    sentiment = {
        "highest_consecutive": max_consecutive,
        "total_limitups": total,
        "consecutive_count": lianban,
        "open_fail_rate": round(open_fail / total * 100, 2) if total else 0,
    }
    if prev_items:
        prev_map = {it["ts_code"]: it for it in prev_items}
        # 晋级率：昨天连板+1 的今天继续
        progressed = 0
        broken = 0
        for it in items:
            prev = prev_map.get(it["ts_code"])
            if not prev:
                continue
            if (prev.get("consecutive") or 1) + 1 == it.get("consecutive"):
                progressed += 1
            if (prev.get("consecutive") or 1) > 1 and (it.get("consecutive") or 1) == 1:
                broken += 1
        total_prev_lian = len([i for i in prev_items if (i.get("consecutive") or 1) > 1])
        sentiment.update(
            {
                "progress_rate": round(progressed / total_prev_lian * 100, 2) if total_prev_lian else None,
                "break_rate": round(broken / total_prev_lian * 100, 2) if total_prev_lian else None,
            }
        )
    return sentiment


def refresh(date: str) -> Tuple[str, List[Dict]]:
    provider = DefaultDataProvider()
    target_date = to_date_str(date)
    cache.init_db()

    limitups = provider.get_limit_up_pool(target_date)
    lhb_items = tag_hot_money(provider.get_lhb(target_date))
    lhb_codes = {it["ts_code"] for it in lhb_items}
    for it in limitups:
        it["lhb_flag"] = it.get("ts_code") in lhb_codes
        it["hot_money_flag"] = any(kw in json.dumps(lhb_items, ensure_ascii=False) for kw in _load_hot_keywords())

    cache.upsert_limitups(target_date, limitups)
    cache.upsert_lhb(target_date, lhb_items)

    for it in limitups:
        start = default_start_date(target_date)
        klines = provider.get_kline(it["ts_code"], start, target_date)
        cache.upsert_kline(it["ts_code"], klines)

    return target_date, limitups
