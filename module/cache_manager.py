import os
import json
import time
from datetime import datetime

class CacheManager:
    def __init__(self, cache_file, market_open_time, market_close_time, cache_duration=3600):
        # 캐시 파일이 저장될 디렉토리를 설정 (기본: cache)
        self.cache_dir = "cache"
        # 캐시 디렉토리가 존재하지 않으면 생성
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            print(f"[DEBUG] 캐시 디렉토리 {self.cache_dir} 생성됨.")
        
        # 캐시 파일 경로 설정
        self.cache_file = os.path.join(self.cache_dir, cache_file)
        self.market_open_time = market_open_time
        self.market_close_time = market_close_time
        self.cache_duration = cache_duration  # 캐시 유효 기간 (초 단위)

    def is_market_open(self):
        """
        현재 시간이 마켓의 개장 시간에 해당하는지 확인합니다.
        - 금요일 15:30 이후나 주말은 폐장으로 처리
        - 개장 시간 내에 있는 경우 True, 폐장 시간인 경우 False를 반환
        """
        now = datetime.now()
        print(f"[DEBUG] 현재 시간: {now}")
        
        # 금요일 15:30 이후는 폐장 상태로 처리
        if now.weekday() == 4 and now.time() > self.market_close_time.time():
            print("[DEBUG] 금요일 15:30 이후로 폐장 상태입니다.")
            return False
        # 주말(토요일, 일요일)은 폐장 상태로 처리
        if now.weekday() in [5, 6]:
            print("[DEBUG] 토요일 또는 일요일로 폐장 상태입니다.")
            return False
        
        # 개장 시간 범위에 해당하면 True 반환
        if self.market_open_time.time() <= now.time() <= self.market_close_time.time():
            print("[DEBUG] 현재 마켓은 개장 상태입니다.")
            return True
        else:
            print("[DEBUG] 현재 마켓은 폐장 상태입니다.")
            return False

    def load_cache(self):
        """
        캐시 파일을 로드하여 내용을 반환합니다.
        캐시 파일이 존재하지 않으면 None을 반환합니다.
        """
        if os.path.exists(self.cache_file):
            print(f"[DEBUG] 캐시 파일 {self.cache_file} 이(가) 존재합니다.")
            with open(self.cache_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        print("[DEBUG] 캐시 파일이 존재하지 않습니다.")
        return None

    def save_cache(self, data):
        """
        데이터를 캐시 파일에 저장합니다.
        """
        with open(self.cache_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)
        print(f"[DEBUG] 캐시 파일 {self.cache_file} 에 데이터를 저장했습니다.")

    def is_cache_valid(self):
        """
        캐시 파일이 유효한지 판단합니다.
        - 캐시 파일의 나이가 cache_duration을 초과하면 만료된 것으로 간주
        - 마켓이 개장 상태일 때는 캐시를 갱신하고, 폐장 상태일 때는 캐시 데이터를 사용
        """
        if os.path.exists(self.cache_file):
            # 캐시 파일의 생성/수정 후 경과 시간(초)을 계산
            cache_age = time.time() - os.path.getmtime(self.cache_file)
            print(f"[DEBUG] 캐시 파일 나이: {cache_age:.2f}초")
            
            # 캐시가 만료되었는지 확인
            if cache_age > self.cache_duration:
                print("[DEBUG] 캐시가 만료되었습니다.")
                return False
            
            # 캐시 데이터 로드
            cache_data = self.load_cache()
            if cache_data and cache_data.get('marketStatus') == 'CLOSE':
                # 마켓이 폐장 상태일 때 캐시를 사용
                if not self.is_market_open():
                    print("[DEBUG] 마켓이 폐장 상태이며, 캐시 데이터를 사용할 수 있습니다.")
                    return True
                else:
                    print("[DEBUG] 마켓이 개장 상태이므로 캐시 데이터를 사용할 수 없습니다.")
        else:
            print("[DEBUG] 캐시 파일이 존재하지 않거나 유효하지 않습니다.")
        return False

    def get_cached_data(self):
        """
        캐시된 데이터를 반환합니다.
        - 캐시된 데이터가 있으면 반환하고, 없으면 None 반환
        """
        cache_data = self.load_cache()
        if cache_data:
            print("[DEBUG] 캐시된 데이터를 반환합니다.")
            return cache_data.get('result')
        print("[DEBUG] 캐시된 데이터가 없습니다.")
        return None
