import os
import json
from datetime import datetime, time
import pytz

class CacheManager:
    def __init__(self, cache_dir, cache_file_prefix):
        self.cache_dir = cache_dir
        self.cache_file_prefix = cache_file_prefix

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_file_path(self, stock_code):
        return os.path.join(self.cache_dir, f"{self.cache_file_prefix}_{stock_code}_cache.json")

    def load_cache(self, stock_code):
        cache_file = self._get_cache_file_path(stock_code)
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        return None

    def save_cache(self, stock_code, data):
        cache_file = self._get_cache_file_path(stock_code)
        with open(cache_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)


    def is_cache_valid(self, stock_code):
        # 타임존 설정
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        day_of_week = now.weekday()  # 0: 월요일, 1: 화요일, ..., 6: 일요일

        # 캐시 파일의 경로를 가져옵니다.
        cache_file = self._get_cache_file_path(stock_code)

        # 장 상태를 확인합니다.
        from module.naver_upjong_quant import check_market_status
        market_status = check_market_status(market='KOSPI')

        # 장중일 경우 캐시는 유효하지 않음
        if market_status != 'CLOSE':
            return False

        # 캐시 파일이 존재하는지 확인합니다.
        if not os.path.exists(cache_file):
            return False

        # 캐시 파일의 마지막 수정 시간을 가져옵니다.
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file), kst)

        # 주말 여부 확인
        is_weekend = day_of_week >= 5

        # 영업일 계산
        def get_last_trading_day(date):
            while date.weekday() >= 5:
                date -= datetime.timedelta(days=1)
            return date

        last_trading_day = get_last_trading_day(now)

        # 16:30 설정
        close_time = time(16, 30)
        
        # 타임존을 포함하여 last_trading_day_end 생성
        last_trading_day_end = datetime.combine(last_trading_day, close_time, kst)

        # 주말인 경우 금요일 16:30 이후 생성된 캐시를 유효하게 처리
        if is_weekend and last_trading_day_end < file_mod_time:
            return True

        # 마지막 거래일 16:30 이후에 생성된 캐시는 유효하지 않음
        if file_mod_time > last_trading_day_end:
            return False

        return True
