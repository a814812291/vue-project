import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cache.db")
DB_PATH = os.path.abspath(DB_PATH)


@contextmanager
def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS limit_list_d (
                trade_date TEXT,
                ts_code TEXT,
                name TEXT,
                pct_chg REAL,
                amount REAL,
                fd_amount REAL,
                first_time TEXT,
                last_time TEXT,
                open_times INTEGER,
                consecutive INTEGER,
                industry TEXT,
                reason TEXT,
                lhb_flag INTEGER,
                hot_money_flag INTEGER,
                raw_json TEXT,
                PRIMARY KEY(trade_date, ts_code)
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS daily (
                ts_code TEXT,
                trade_date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                vol REAL,
                amount REAL,
                PRIMARY KEY(ts_code, trade_date)
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lhb (
                trade_date TEXT,
                ts_code TEXT,
                reason TEXT,
                buy REAL,
                sell REAL,
                net REAL,
                raw_json TEXT,
                PRIMARY KEY(trade_date, ts_code, reason)
            );
            """
        )


def upsert_limitups(trade_date: str, items: List[Dict]):
    with get_conn() as conn:
        for it in items:
            conn.execute(
                """
                INSERT OR REPLACE INTO limit_list_d VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    trade_date,
                    it.get("ts_code"),
                    it.get("name"),
                    it.get("pct_chg"),
                    it.get("amount"),
                    it.get("fd_amount"),
                    it.get("first_time"),
                    it.get("last_time"),
                    it.get("open_times"),
                    it.get("consecutive"),
                    it.get("industry"),
                    it.get("reason"),
                    int(bool(it.get("lhb_flag"))),
                    int(bool(it.get("hot_money_flag"))),
                    json.dumps(it.get("raw_json", {}), ensure_ascii=False),
                ),
            )


def upsert_lhb(trade_date: str, items: List[Dict]):
    with get_conn() as conn:
        for it in items:
            conn.execute(
                """
                INSERT OR REPLACE INTO lhb VALUES(?,?,?,?,?,?,?)
                """,
                (
                    trade_date,
                    it.get("ts_code"),
                    it.get("reason"),
                    it.get("buy"),
                    it.get("sell"),
                    it.get("net"),
                    json.dumps(it.get("raw_json", {}), ensure_ascii=False),
                ),
            )


def upsert_kline(ts_code: str, prices: List[Dict]):
    with get_conn() as conn:
        for bar in prices:
            conn.execute(
                """
                INSERT OR REPLACE INTO daily VALUES(?,?,?,?,?,?,?,?)
                """,
                (
                    ts_code,
                    bar.get("trade_date"),
                    bar.get("open"),
                    bar.get("high"),
                    bar.get("low"),
                    bar.get("close"),
                    bar.get("vol"),
                    bar.get("amount"),
                ),
            )


def query_limitups(date: str) -> List[Dict]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM limit_list_d WHERE trade_date=? ORDER BY fd_amount DESC", (date,)
        )
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    results = []
    for row in rows:
        item = dict(zip(cols, row))
        item["lhb_flag"] = bool(item.get("lhb_flag"))
        item["hot_money_flag"] = bool(item.get("hot_money_flag"))
        results.append(item)
    return results


def query_lhb(date: str) -> List[Dict]:
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM lhb WHERE trade_date=?", (date,))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def query_kline(ts_code: str, start: str, end: str) -> List[Dict]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM daily WHERE ts_code=? AND trade_date BETWEEN ? AND ? ORDER BY trade_date",
            (ts_code, start, end),
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def has_limitups(date: str) -> bool:
    with get_conn() as conn:
        cur = conn.execute("SELECT 1 FROM limit_list_d WHERE trade_date=? LIMIT 1", (date,))
        return cur.fetchone() is not None


def last_available_date() -> Optional[str]:
    with get_conn() as conn:
        cur = conn.execute("SELECT trade_date FROM limit_list_d ORDER BY trade_date DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            return row[0]
        return None
