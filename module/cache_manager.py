import json
from datetime import datetime, time, timedelta
import pytz
import os


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

        # 장 상태를 확인합니다.
        from module.naver_upjong_quant import check_market_status
        market_status = check_market_status(market='KOSPI')

        # 1. 장중일 경우 캐시는 유효하지 않음
        if market_status != 'CLOSE':
            return False

        # 2. 우선 캐시의 생성시간을 가져온다.
        cache_file = self._get_cache_file_path(stock_code)

        if not os.path.exists(cache_file):
            print("[DEBUG] 유효한 캐시가 없으므로 데이터를 호출합니다.")
            return False

        file_mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file), kst)

        # 16:30 설정
        close_time = time(16, 30)
        
        # 3. 휴장일 예외 처리
        # 평일이고 09시~16시 30분 사이임에도 market_status가 CLOSE라면 휴장일로 처리
        if day_of_week < 5 and time(9, 0) <= now.time() <= close_time and market_status == 'CLOSE':
            print("[DEBUG] 휴장일로 추정됩니다.")
            print("[DEBUG] 평일 장운영시간 이지만 [장마감상태].")
            # 전일 16:30 이후 생성된 캐시를 유효하게 처리
            last_trading_day = now - timedelta(days=1)
            # 만약 휴장이 월요일이라면, 금요일로 돌아가서 처리
            if day_of_week == 0:
                last_trading_day = now - timedelta(days=3)  # 금요일

            last_trading_day_close_time = datetime.combine(last_trading_day.date(), close_time, kst)
            if file_mod_time > last_trading_day_close_time:
                return True
            else:
                return False

        # 4. 월요일 0시부터 8시까지는 주말과 동일하게 처리
        if day_of_week == 0 and now.time() < time(8, 0):  # 월요일, 0시~8시
            last_friday = now - timedelta(days=3)  # 지난 금요일
            last_friday_close_time = datetime.combine(last_friday.date(), close_time, kst)
            if file_mod_time > last_friday_close_time:
                return True
            else:
                return False

        # 5. 평일인 경우 캐시가 당일 16시 30분 이후에 생성됐다면 유효캐시임
        if day_of_week < 5:  # 월요일~금요일
            today_close_time = datetime.combine(now.date(), close_time, kst)
            if file_mod_time > today_close_time:
                return True
            else:
                return False

        # 6. 조회일이 주말인 경우
        if day_of_week >= 5:  # 토요일~일요일
            # 캐시가 금요일 16시 30분 이후 생성된 캐시라면 유효캐시다
            last_friday = now - timedelta(days=day_of_week - 4)  # 지난 금요일
            last_friday_close_time = datetime.combine(last_friday.date(), close_time, kst)
            if file_mod_time > last_friday_close_time:
                return True
            else:
                return False
