import os
import json
import datetime, time
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
        """
        주어진 종목 코드에 대한 캐시 파일의 유효성을 검사합니다.
        
        Parameters:
            stock_code (str): 종목 코드.

        Returns:
            bool: 캐시가 유효하면 True, 그렇지 않으면 False.
        """
        
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.datetime.now(kst)
        day_of_week = now.weekday()  # 0: 월요일, 1: 화요일, ..., 6: 일요일
        current_time = now.time()    # 현재 시간

        # 주어진 종목 코드에 해당하는 캐시 파일의 경로를 가져옵니다.
        cache_file = self._get_cache_file_path(stock_code)

        # 서울 시간대 설정
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.datetime.now(kst)
        # day_of_week = now.weekday()  # 0: 월요일, 1: 화요일, ..., 6: 일요일
        # current_time = now.time()    # 현재 시간

        # 주어진 종목 코드에 해당하는 캐시 파일의 경로를 가져옵니다.
        cache_file = self._get_cache_file_path(stock_code)
        print(f"[DEBUG] 캐시 파일 경로: {cache_file}")

        # 장 상태를 확인합니다.
        from module.naver_upjong_quant import check_market_status
        market_status = check_market_status(market='KOSPI')
        print(f"[DEBUG] 현재 장 상태: {market_status}")

        # 장중(마켓 OPEN)인 경우 캐시는 유효합니다.
        if market_status != 'CLOSE':
            print("[DEBUG] 장이 개장 중이므로 캐시가 유효함.")
            return True

        # 캐시 파일이 존재하는지 확인합니다.
        if not os.path.exists(cache_file):
            print(f"[DEBUG] 캐시 파일이 존재하지 않음: {cache_file}")
            return False

        # 캐시 파일의 마지막 수정 시간을 가져옵니다.
        file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(cache_file), kst)
        print(f"[DEBUG] 캐시 파일의 마지막 수정 시간: {file_mod_time}")

        # 오늘이 주말인지 확인합니다.
        is_weekend = now.weekday() >= 5  # 토요일(5) 또는 일요일(6) 여부
        print(f"[DEBUG] 오늘은 주말인가요? {'예' if is_weekend else '아니오'}")


        # 영업일 계산
        def get_last_trading_day(date):
            """주말과 공휴일을 제외한 마지막 거래일을 계산합니다."""
            while date.weekday() >= 5:  # 주말인 경우
                date -= datetime.timedelta(days=1)
            return date

        # 오늘의 마지막 거래일을 계산합니다.
        last_trading_day = get_last_trading_day(now)
        print(f"[DEBUG] 오늘의 마지막 거래일: {last_trading_day}")

        # 평일의 경우 전일 거래일로 설정
        if not is_weekend:
            last_trading_day -= datetime.timedelta(days=1)  # 전일 거래일로 설정
            print(f"[DEBUG] 평일이므로 마지막 거래일을 전일로 설정: {last_trading_day}")
        
        # 주말의 경우 금요일 거래일로 설정
        else:
            last_trading_day -= datetime.timedelta(days=(last_trading_day.weekday() - 4))  # 금요일로 설정
            print(f"[DEBUG] 주말이므로 마지막 거래일을 금요일로 설정: {last_trading_day}")

        # 16:30 설정
        close_time = datetime.time(16, 30)
        # 마지막 거래일의 16:30 시간을 추가합니다.
        last_trading_day_end = datetime.datetime.combine(last_trading_day, close_time, kst)
        print(f"[DEBUG] 마지막 거래일의 16:30 시간: {last_trading_day_end}")

        # 마지막 거래일 16:30 이후에 생성된 캐시는 유효하지 않음
        if file_mod_time > last_trading_day_end:
            print("[DEBUG] 캐시 파일의 수정일이 마지막 거래일의 16:30 이후입니다. 캐시가 유효하지 않음.")
            return False

        # 캐시 파일이 존재하고 유효한 경우
        print("[DEBUG] 캐시 파일이 존재하고 유효함.")
        return True