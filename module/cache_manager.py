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
        market_open_time = time(9, 0)
        market_close_time = time(16, 40)

        # 장 상태와 마지막 거래일자 및 시간 정보를 확인합니다.
        from module.naver_stock_util import check_market_status
        market_status, last_traded_at = check_market_status(nation_code)

        print(f"[DEBUG] 조회 국가 코드 : {nation_code}")
        print(f"[DEBUG] 마켓 상태: {market_status}, 마지막 거래일자: {last_traded_at}")

        # 캐시 파일 경로 확인
        cache_file = self._get_cache_file_path(stock_code)

        if os.path.exists(cache_file):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file), kst)
            print(f"[DEBUG] 캐시 생성 시간: {file_mod_time}")
        else:
            print("[DEBUG] 유효한 캐시가 없으므로 데이터를 호출합니다.")
            return False

        # 한국 주식일 때만 16:30 설정
        if nation_code == 'KOR':
            close_time = time(16, 30)

            # 마지막 거래일자 및 시간을 처리
            if isinstance(last_traded_at, datetime):
                last_trading_day = last_traded_at
            else:
                last_trading_day = datetime.strptime(last_traded_at, "%Y-%m-%dT%H:%M:%S%z").astimezone(kst)

            last_trading_day_close_time = datetime.combine(last_trading_day.date(), close_time, kst)

            # 한국 주식의 경우
            if market_status == 'OPEN':
                # 장중일 때는 5분 이내 캐시가 유효
                if (now - file_mod_time) < timedelta(minutes=5):
                    print(f"[DEBUG] 장중이며 5분 이내 생성된 캐시가 있습니다. 유효 처리됩니다. (생성 시각: {file_mod_time})")
                    return True
                print("[DEBUG] 장중이지만 캐시가 유효하지 않습니다.")
                return False

            if market_status == 'CLOSE':
                # 개장시간 내에 CLOSE 상태로, 마지막 거래일자가 오늘보다 이전이며 현재 요일이 평일인 경우 휴장일로 간주
                if market_open_time <= now.time() <= market_close_time and last_trading_day.date() < now.date() and day_of_week < 5:
                    print(f"[DEBUG] 개장시간 내 CLOSE 상태이며, 마지막 거래일자가 오늘보다 이전이고 현재 요일이 평일입니다. 휴장일로 간주.")
                    return False

                # 장 마감 이후 생성된 캐시가 유효
                if file_mod_time > last_trading_day_close_time:
                    print(f"[DEBUG] 장 마감 이후 생성된 캐시. 유효 처리됩니다.")
                    return True

                # 금요일 장 마감 이후 ~ 주말 및 월요일 0시 ~ 8시까지는 금요일 16시 30분 이후 생성된 캐시가 유효
                if day_of_week == 0 and now.time() < time(8, 0):
                    last_friday = now - timedelta(days=3)  # 지난 금요일
                    last_friday_close_time = datetime.combine(last_friday.date(), close_time, kst)
                    if file_mod_time > last_friday_close_time:
                        print(f"[DEBUG] 월요일 0시~8시까지 금요일 장 마감 이후 생성된 캐시. 유효 처리됩니다.")
                        return True
                    print("[DEBUG] 월요일 0시~8시까지 생성된 캐시가 금요일 장 마감 이후가 아닙니다.")
                    return False

                # 평일의 경우 장 마감 이후 생성된 캐시가 유효
                if day_of_week < 5:
                    today_close_time = datetime.combine(now.date(), close_time, kst)
                    if file_mod_time > today_close_time:
                        print(f"[DEBUG] 평일 장 마감 이후 생성된 캐시. 유효 처리됩니다.")
                        return True
                    print("[DEBUG] 평일 장 마감 이후 생성된 캐시가 아닙니다.")
                    return False

                # 주말의 경우, 금요일 장 마감 이후 생성된 캐시가 유효
                if day_of_week >= 5:
                    last_friday = now - timedelta(days=day_of_week - 4)  # 지난 금요일
                    last_friday_close_time = datetime.combine(last_friday.date(), close_time, kst)
                    if file_mod_time > last_friday_close_time:
                        print(f"[DEBUG] 주말의 경우 금요일 장 마감 이후 생성된 캐시. 유효 처리됩니다.")
                        return True
                    print("[DEBUG] 주말에 생성된 캐시가 금요일 장 마감 이후가 아닙니다.")
                    return False

        # 해외 주식의 경우
        else:
            # 해외 주식은 장중에 캐시를 유효하지 않다고 가정
            if market_status == 'OPEN':
                print("[DEBUG] 해외 주식은 장중에 캐시를 유효하지 않다고 가정합니다.")
                return False

            # 해외 주식은 장 마감 이후 유효 처리
            if market_status == 'CLOSE':
                if isinstance(last_traded_at, datetime):
                    last_trading_day = last_traded_at
                else:
                    last_trading_day = datetime.strptime(last_traded_at, "%Y-%m-%dT%H:%M:%S%z").astimezone(kst)

                last_trading_day_close_time = datetime.combine(last_trading_day.date(), time(16, 30), kst)
                if file_mod_time > last_trading_day_close_time:
                    print(f"[DEBUG] 해외 주식의 마지막 거래일 {last_trading_day} 이후 생성된 캐시. 유효 처리됩니다.")
                    return True

                # 해외 주식은 평일, 주말 구분 없이 장 마감 이후 유효 처리
                if day_of_week < 5:
                    today_close_time = datetime.combine(now.date(), time(16, 30), kst)
                    if file_mod_time > today_close_time:
                        print(f"[DEBUG] 평일 장 마감 이후 생성된 해외 주식 캐시. 유효 처리됩니다.")
                        return True
                    print("[DEBUG] 평일 장 마감 이후 생성된 해외 주식 캐시가 아닙니다.")
                    return False

                if day_of_week >= 5:
                    last_friday = now - timedelta(days=day_of_week - 4)  # 지난 금요일
                    last_friday_close_time = datetime.combine(last_friday.date(), time(16, 30), kst)
                    if file_mod_time > last_friday_close_time:
                        print(f"[DEBUG] 주말의 경우 금요일 장 마감 이후 생성된 해외 주식 캐시. 유효 처리됩니다.")
                        return True
                    print("[DEBUG] 주말에 생성된 해외 주식 캐시가 금요일 장 마감 이후가 아닙니다.")
                    return False

        print("[DEBUG] 유효한 캐시가 아닙니다. 새 데이터를 호출합니다.")
        return False
