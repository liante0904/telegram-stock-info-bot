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

def is_cache_valid(self, stock_code, nation_code):
    # 타임존 설정
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    day_of_week = now.weekday()  # 0: 월요일, 1: 화요일, ..., 6: 일요일

    # 장 상태와 마지막 거래일 정보를 확인합니다.
    from module.naver_stock_util import check_market_status
    market_status, last_traded_at = check_market_status(nation_code)
    print(market_status, last_traded_at)
    
    # 캐시 파일 경로 확인
    cache_file = self._get_cache_file_path(stock_code)
    
    if os.path.exists(cache_file):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file), kst)
    else:
        print("[DEBUG] 유효한 캐시가 없으므로 데이터를 호출합니다.")
        return False

    # 16:30 설정
    close_time = time(16, 30)

    # 마지막 거래일 정보를 처리
    if isinstance(last_traded_at, datetime):
        last_trading_day = last_traded_at
    else:
        last_trading_day = datetime.strptime(last_traded_at, "%Y-%m-%dT%H:%M:%S%z").astimezone(kst)
    
    last_trading_day_close_time = datetime.combine(last_trading_day.date(), close_time, kst)

    # 1. 장중일 경우 캐시는 유효하지 않음
    if market_status == 'OPEN':
        # 장중인데 5분 이내 캐시가 존재하면 유효
        if (now - file_mod_time) < timedelta(minutes=5):
            print(f"[DEBUG] 장중이며 5분 이내 생성된 캐시가 있습니다. 유효 처리됩니다. (생성 시각: {file_mod_time})")
            return True
        # 장중인데 캐시가 유효하지 않음
        return False

    # 2. 장이 닫힌 상태(마감 또는 휴장)
    if market_status == 'CLOSE':
        if file_mod_time > last_trading_day_close_time:
            print(f"[DEBUG] 마지막 거래일 {last_trading_day} 이후 생성된 캐시. 유효 처리됩니다.")
            return True
        
        # 4. 평일(월~금) 중 장이 열리지 않은 경우 (휴장일)
        if day_of_week < 5:
            print(f"[DEBUG] 평일 휴장일로 추정됩니다. 마지막 거래일: {last_trading_day}")
            if file_mod_time > last_trading_day_close_time:
                return True
            else:
                return False

    # 5. 월요일 0시~8시까지는 주말과 동일하게 처리
    if day_of_week == 0 and now.time() < time(8, 0):
        last_friday = now - timedelta(days=3)  # 지난 금요일
        last_friday_close_time = datetime.combine(last_friday.date(), close_time, kst)
        if file_mod_time > last_friday_close_time:
            return True
        else:
            return False

    # 6. 평일 중 당일 장 마감 이후
    if day_of_week < 5:
        today_close_time = datetime.combine(now.date(), close_time, kst)
        if file_mod_time > today_close_time:
            return True
        else:
            return False

    # 7. 주말 처리
    if day_of_week >= 5:
        last_friday = now - timedelta(days=day_of_week - 4)  # 지난 금요일
        last_friday_close_time = datetime.combine(last_friday.date(), close_time, kst)
        if file_mod_time > last_friday_close_time:
            return True
        else:
            return False

    print("[DEBUG] 유효한 캐시가 아닙니다. 새 데이터를 호출합니다.")
    return False
