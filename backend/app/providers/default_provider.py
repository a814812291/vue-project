import json
import logging
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import requests

from .base import DataProvider
from ..utils.dates import to_date_str

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"
}


def _safe_request(url: str, params=None, timeout=8, retries=2):
    params = params or {}
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=timeout, headers=HEADERS)
            resp.raise_for_status()
            return resp
        except Exception as exc:  # pragma: no cover - network fallback
            logger.warning("request failed %s %s/%s", url, attempt + 1, retries, exc_info=exc)
            time.sleep(1)
    return None


class DefaultDataProvider(DataProvider):
    """Provider with network fetch + offline fallback samples."""

    def __init__(self):
        self.sample_data = self._load_sample_limitups()

    def _load_sample_limitups(self):
        # Sample data ensures offline availability
        return [
            {
                "ts_code": "600000.SH",
                "name": "浦发银行",
                "pct_chg": 10.01,
                "amount": 123000000,
                "fd_amount": 56000000,
                "first_time": "09:35",
                "last_time": "14:50",
                "open_times": 1,
                "consecutive": 1,
                "industry": "银行",
                "reason": "金融改革;数字货币",
                "lhb_flag": False,
                "hot_money_flag": False,
                "raw_json": {},
            },
            {
                "ts_code": "300750.SZ",
                "name": "宁德时代",
                "pct_chg": 10.0,
                "amount": 4500000000,
                "fd_amount": 800000000,
                "first_time": "09:31",
                "last_time": "15:00",
                "open_times": 0,
                "consecutive": 2,
                "industry": "电池",
                "reason": "锂电池;储能",
                "lhb_flag": True,
                "hot_money_flag": True,
                "raw_json": {},
            },
            {
                "ts_code": "000001.SZ",
                "name": "平安银行",
                "pct_chg": 10.02,
                "amount": 980000000,
                "fd_amount": 300000000,
                "first_time": "10:12",
                "last_time": "14:30",
                "open_times": 2,
                "consecutive": 3,
                "industry": "银行",
                "reason": "金融;国企改革",
                "lhb_flag": True,
                "hot_money_flag": False,
                "raw_json": {},
            },
        ]

    def get_limit_up_pool(self, date: str) -> List[Dict]:
        # Attempt Eastmoney limit up API (fast jsonp) with fallback
        date_fmt = to_date_str(date)
        url = "https://push2ex.eastmoney.com/getTopicZTPool"  # unofficial but stable
        params = {
            "ut": "b2884a393a59ad64002292a3e90d46a5",
            "dpt": "wz.ztzt",
            "Pageindex": 0,
            "pagesize": 200,
            "sort": "fbt:asc",
            "date": date_fmt,
            "_=": int(time.time() * 1000),
        }
        resp = _safe_request(url, params=params)
        if resp and "data" in resp.text:
            try:
                json_text = resp.text
                json_text = json_text[json_text.find("(") + 1 : json_text.rfind(")")]
                payload = json.loads(json_text)
                items = payload.get("data", {}).get("pool", [])
                return [self._map_limitup_item(it) for it in items]
            except Exception:  # pragma: no cover - network path
                logger.exception("parse eastmoney limitup failed")
        logger.info("falling back to sample limit up data")
        return self.sample_data

    def _map_limitup_item(self, it: Dict) -> Dict:
        def _ts(code, mkt):
            return f"{code}.{ 'SH' if mkt == 1 else 'SZ'}"

        return {
            "ts_code": _ts(str(it.get("s")), it.get("m")),
            "name": it.get("n"),
            "pct_chg": it.get("zdp", 0),
            "amount": it.get("amount", 0),
            "fd_amount": it.get("fbt", 0),
            "first_time": it.get("ft"),
            "last_time": it.get("lt"),
            "open_times": it.get("o", 0),
            "consecutive": it.get("lbc", 1),
            "industry": it.get("zttj", ""),
            "reason": it.get("cctj", ""),
            "lhb_flag": False,
            "hot_money_flag": False,
            "raw_json": it,
        }

    def get_lhb(self, date: str) -> List[Dict]:
        date_fmt = to_date_str(date)
        url = "https://push2his.eastmoney.com/api/qt/stock/ffexhislhb/get"
        params = {
            "date": date_fmt,
            "fields1": "f13,f12,f14",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60",
        }
        resp = _safe_request(url, params=params)
        if resp and "data" in resp.text:
            try:
                data = resp.json().get("data", {})
                lhb_list = []
                for item in data.get("diff", []):
                    lhb_list.append(
                        {
                            "ts_code": f"{item.get('f12')}.{'SH' if item.get('f13') == 1 else 'SZ'}",
                            "name": item.get("f14"),
                            "reason": item.get("f51"),
                            "buy": item.get("f52"),
                            "sell": item.get("f53"),
                            "net": item.get("f54"),
                            "raw_json": item,
                        }
                    )
                return lhb_list
            except Exception:  # pragma: no cover
                logger.exception("parse lhb failed")
        logger.info("fallback lhb sample")
        return [
            {
                "ts_code": "300750.SZ",
                "name": "宁德时代",
                "reason": "日涨幅偏离值达7%的证券",
                "buy": 1200000000,
                "sell": 800000000,
                "net": 400000000,
                "raw_json": {},
            }
        ]

    def get_kline(self, code: str, start: str, end: str) -> List[Dict]:
        start_dt = datetime.strptime(start, "%Y%m%d")
        end_dt = datetime.strptime(end, "%Y%m%d")
        delta = (end_dt - start_dt).days
        # Dummy data generation ensures always available
        prices = []
        close = 20.0
        for i in range(max(delta, 50)):
            day = start_dt + timedelta(days=i)
            if day.weekday() >= 5:
                continue
            change = random.uniform(-0.03, 0.03)
            open_price = close * (1 + random.uniform(-0.01, 0.01))
            high = max(open_price, open_price * (1 + abs(change)))
            low = min(open_price, open_price * (1 - abs(change)))
            close = open_price * (1 + change)
            prices.append(
                {
                    "trade_date": day.strftime("%Y%m%d"),
                    "open": round(open_price, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(close, 2),
                    "vol": random.randint(1000000, 9000000),
                    "amount": random.randint(10000000, 90000000),
                }
            )
            if len(prices) >= 260:
                break
        return prices

    def get_ytd_return(self, code: str, date: str) -> Optional[float]:
        # Use generated kline to compute YTD
        date_dt = datetime.strptime(to_date_str(date), "%Y%m%d")
        start_year = datetime(date_dt.year, 1, 1)
        kline = self.get_kline(code, start_year.strftime("%Y%m%d"), date_dt.strftime("%Y%m%d"))
        if not kline:
            return None
        start_price = kline[0]["close"]
        end_price = kline[-1]["close"]
        return round((end_price - start_price) / start_price * 100, 2)

    def get_stock_profile(self, code: str) -> Optional[Dict]:
        return {
            "ts_code": code,
            "name": "样本公司",
            "industry": "样本行业",
            "concepts": ["示例概念", "数字经济"],
            "description": "示例数据源用于离线演示，实际使用可配置为生产接口。",
        }

    def get_shareholders(self, code: str) -> Optional[List[Dict]]:
        return None
