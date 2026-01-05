import logging
from typing import List, Dict

from fastapi import APIRouter, HTTPException

from ..services import cache
from ..services.refresh_service import aggregate_themes, compute_sentiment
from ..utils.dates import to_date_str, default_start_date

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/limitups")
def get_limitups(date: str = "auto"):
    target = to_date_str(date)
    cache.init_db()
    if not cache.has_limitups(target):
        # try fallback date
        last = cache.last_available_date()
        if last:
            target = last
    items = cache.query_limitups(target)
    prev_items: List[Dict] = []
    return {
        "date": target,
        "sentiment": compute_sentiment(items, prev_items),
        "themes": aggregate_themes(items),
        "items": items,
    }


@router.get("/stock/{ts_code}")
def stock_detail(ts_code: str, date: str = "auto"):
    target = to_date_str(date)
    items = cache.query_limitups(target)
    info = next((i for i in items if i.get("ts_code") == ts_code), None)
    if not info:
        raise HTTPException(status_code=404, detail="stock not found")
    lhb_rows = cache.query_lhb(target)
    lhb_info = [i for i in lhb_rows if i.get("ts_code") == ts_code]
    start = default_start_date(target)
    kline = cache.query_kline(ts_code, start, target)
    return {
        "date": target,
        "info": info,
        "kline": kline,
        "lhb": lhb_info,
        "shareholders": None,
        "profile": None,
    }


@router.get("/kline/{ts_code}")
def get_kline(ts_code: str, start: str = "auto", end: str = "auto"):
    end_date = to_date_str(end)
    start_date = default_start_date(end_date)
    prices = cache.query_kline(ts_code, start_date, end_date)
    return {"ts_code": ts_code, "start": start_date, "end": end_date, "prices": prices}


@router.get("/lhb")
def get_lhb(date: str = "auto"):
    target = to_date_str(date)
    cache.init_db()
    if not cache.has_limitups(target):
        last = cache.last_available_date()
        if last:
            target = last
    return {"date": target, "items": cache.query_lhb(target)}
