import json
import sqlite3
from datetime import datetime, timedelta
import pytz
import os

class CacheManager:
    def __init__(self, db_path, cache_table_name="stock_cache"):
        self.db_path = db_path
        self.table_name = cache_table_name
        self._init_table()

    def _init_table(self):
        """SQLite 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                cache_key TEXT PRIMARY KEY,
                data TEXT,
                cached_at TEXT,
                nation_code TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _get_cache_key(self, stock_code, nation_code=None):
        """캐시 키 생성 (stock_code + nation_code 조합)"""
        if nation_code:
            return f"{stock_code}_{nation_code}"
        return stock_code

    def load_cache(self, cache_key):
        """캐시 로드"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT data FROM {self.table_name} WHERE cache_key = ?", (cache_key,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        return None

    def save_cache(self, cache_key, data, nation_code=None):
        """캐시 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT OR REPLACE INTO {self.table_name} (cache_key, data, cached_at, nation_code)
            VALUES (?, ?, ?, ?)
        """, (cache_key, json.dumps(data), datetime.now(pytz.timezone('Asia/Seoul')).isoformat(), nation_code or ''))
        conn.commit()
        conn.close()

    def is_cache_valid(self, cache_key, nation_code=None):
        """캐시 유효성 검사 (간소화)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT cached_at FROM {self.table_name} WHERE cache_key = ?", (cache_key,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False
        
        cached_time = datetime.fromisoformat(row[0])
        now = datetime.now(pytz.timezone('Asia/Seoul'))
        
        # 기본 1시간 유효 (장중에는 5분, 장 마감 후에는 다음날까지)
        if nation_code == 'KOR':
            # 한국 시간 기준
            kst = pytz.timezone('Asia/Seoul')
            now_kst = datetime.now(kst)
            
            # 장 시간 (9:00 ~ 15:30)
            market_open = now_kst.replace(hour=9, minute=0, second=0)
            market_close = now_kst.replace(hour=15, minute=30, second=0)
            
            if market_open <= now_kst <= market_close:
                # 장중: 5분 유효
                return (now - cached_time) < timedelta(minutes=5)
            else:
                # 장 마감: 24시간 유효
                return (now - cached_time) < timedelta(hours=24)
        else:
            # 해외 주식: 1시간 유효
            return (now - cached_time) < timedelta(hours=1)

    def clear_expired_cache(self, max_age_hours=24):
        """만료된 캐시 정리"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cutoff = (datetime.now(pytz.timezone('Asia/Seoul')) - timedelta(hours=max_age_hours)).isoformat()
        cursor.execute(f"DELETE FROM {self.table_name} WHERE cached_at < ?", (cutoff,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted
