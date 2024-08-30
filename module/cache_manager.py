import os
import json
import time
from datetime import datetime

class CacheManager:
    def __init__(self, cache_file, market_open_time, market_close_time, cache_duration=3600):
        # 캐시 경로를 cache 폴더로 설정
        self.cache_dir = "cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            print(f"[DEBUG] 캐시 디렉토리 {self.cache_dir} 생성됨.")
        
        self.cache_file = os.path.join(self.cache_dir, cache_file)
        self.market_open_time = market_open_time
        self.market_close_time = market_close_time
        self.cache_duration = cache_duration  # 캐시 유효 기간 (초 단위)

    def is_market_open(self):
        now = datetime.now()
        print(f"[DEBUG] 현재 시간: {now}")
        
        if now.weekday() == 4 and now.time() > self.market_close_time.time():
            print("[DEBUG] 금요일 15:30 이후로 폐장 상태입니다.")
            return False
        if now.weekday() in [5, 6]:  # 토, 일
            print("[DEBUG] 토요일 또는 일요일로 폐장 상태입니다.")
            return False
        
        if self.market_open_time.time() <= now.time() <= self.market_close_time.time():
            print("[DEBUG] 현재 마켓은 개장 상태입니다.")
            return True
        else:
            print("[DEBUG] 현재 마켓은 폐장 상태입니다.")
            return False

    def load_cache(self):
        if os.path.exists(self.cache_file):
            print(f"[DEBUG] 캐시 파일 {self.cache_file} 이(가) 존재합니다.")
            with open(self.cache_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        print("[DEBUG] 캐시 파일이 존재하지 않습니다.")
        return None

    def save_cache(self, data):
        with open(self.cache_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)
        print(f"[DEBUG] 캐시 파일 {self.cache_file} 에 데이터를 저장했습니다.")

    def is_cache_valid(self):
        if os.path.exists(self.cache_file):
            cache_age = time.time() - os.path.getmtime(self.cache_file)
            print(f"[DEBUG] 캐시 파일 나이: {cache_age:.2f}초")
            if cache_age > self.cache_duration:
                print("[DEBUG] 캐시가 만료되었습니다.")
                return False
            
            cache_data = self.load_cache()
            if cache_data and cache_data.get('marketStatus') == 'CLOSE':
                if not self.is_market_open():
                    print("[DEBUG] 마켓이 폐장 상태이며, 캐시 데이터를 사용할 수 있습니다.")
                    return True
                else:
                    print("[DEBUG] 마켓이 개장 상태이므로 캐시 데이터를 사용할 수 없습니다.")
        else:
            print("[DEBUG] 캐시 파일이 존재하지 않거나 유효하지 않습니다.")
        return False

    def get_cached_data(self):
        cache_data = self.load_cache()
        if cache_data:
            print("[DEBUG] 캐시된 데이터를 반환합니다.")
            return cache_data.get('result')
        print("[DEBUG] 캐시된 데이터가 없습니다.")
        return None
