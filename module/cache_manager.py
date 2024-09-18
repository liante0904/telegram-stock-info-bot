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
            json.dump(data, file, ensure_ascii=False, indent=4)

    def is_cache_valid(self, stock_code):
        # 타임존 설정
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        day_of_week = now.weekday()  # 0: 월요일, 1: 화요일, ..., 6: 일요일

        # 장 상태와 마지막 거래일 정보를 확인합니다.
        from module.naver_stock_util import check_market_status
        market_status, last_traded_at = check_market_status(market='KOSPI')

        # 1. 장중일 경우 캐시는 유효하지 않음
        if market_status == 'OPEN':
            cache_file = self._get_cache_file_path(stock_code)

            if os.path.exists(cache_file):
                file_mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file), kst)
                # 파일이 생성된 후 5분 이내인지 확인
                if (now - file_mod_time) < timedelta(minutes=5):
                    print(f"[DEBUG] 장중이며 5분 이내 생성된 캐시가 있습니다. 유효 처리됩니다. (생성 시각: {file_mod_time})")
                    return True

            # 장중이지만 캐시는 유효하지 않음
            return False

        # 2. 장마감 또는 휴장일 처리
        cache_file = self._get_cache_file_path(stock_code)

        if not os.path.exists(cache_file):
            print("[DEBUG] 유효한 캐시가 없으므로 데이터를 호출합니다.")
            return False

        file_mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file), kst)

        # 16:30 설정
        close_time = time(16, 30)

        # 3. 마지막 거래일 정보를 바탕으로 휴장일 처리
        if isinstance(last_traded_at, datetime):
            last_trading_day = last_traded_at
        else:
            last_trading_day = datetime.strptime(last_traded_at, "%Y-%m-%dT%H:%M:%S%z").astimezone(kst)

        last_trading_day_close_time = datetime.combine(last_trading_day.date(), close_time, kst)

        # 캐시 파일이 마지막 거래일 이후에 생성되었는지 확인
        if file_mod_time > last_trading_day_close_time:
            print(f"[DEBUG] 마지막 거래일 {last_trading_day} 이후 생성된 캐시. 유효 처리됩니다.")
            return True

        # 4. 휴장일(예: 명절) 처리
        # 평일(월~금) 중 장이 열리지 않은 경우에도 전 거래일을 기준으로 캐시를 처리
        if market_status == 'CLOSE' and day_of_week < 5:
            print(f"[DEBUG] 휴장일로 추정됩니다. 마지막 거래일: {last_trading_day}")
            if file_mod_time > last_trading_day_close_time:
                return True
            else:
                return False

        # 5. 월요일 0시부터 8시까지는 주말과 동일하게 처리
        if day_of_week == 0 and now.time() < time(8, 0):  # 월요일, 0시~8시
            last_friday = now - timedelta(days=3)  # 지난 금요일
            last_friday_close_time = datetime.combine(last_friday.date(), close_time, kst)
            if file_mod_time > last_friday_close_time:
                return True
            else:
                return False

        # 6. 평일인 경우 캐시가 당일 16시 30분 이후에 생성됐다면 유효캐시임
        if day_of_week < 5:  # 월요일~금요일
            today_close_time = datetime.combine(now.date(), close_time, kst)
            if file_mod_time > today_close_time:
                return True
            else:
                return False

        # 7. 조회일이 주말인 경우
        if day_of_week >= 5:  # 토요일~일요일
            # 캐시가 금요일 16시 30분 이후 생성된 캐시라면 유효캐시다
            last_friday = now - timedelta(days=day_of_week - 4)  # 지난 금요일
            last_friday_close_time = datetime.combine(last_friday.date(), close_time, kst)
            if file_mod_time > last_friday_close_time:
                return True
            else:
                return False

        print("[DEBUG] 유효한 캐시가 아닙니다. 새 데이터를 호출합니다.")
        return False