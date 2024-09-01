import os
import json
import time


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
        
        # 주어진 종목 코드에 해당하는 캐시 파일의 경로를 가져옵니다.
        cache_file = self._get_cache_file_path(stock_code)
        
        # 캐시 파일이 존재하는지 확인합니다.
        if os.path.exists(cache_file):
            from module.naver_upjong_quant import check_market_status
            # 캐시 파일이 존재하는 경우, marketStatus가 "CLOSE"인지 확인합니다.
            # 장이 "CLOSE" 상태가 아니면 캐시가 유효하지 않다고 판단합니다.
            if check_market_status(market='KOSPI') != 'CLOSE':
                print("[DEBUG] 장이 개장 중이므로 캐시가 유효하지 않음.")
                return False
            
            # 장이 "CLOSE" 상태이고, 캐시 파일이 존재하면 캐시가 유효하다고 판단합니다.
            print("[DEBUG] 장이 폐장 중이므로 캐시가 유효함.")
            return True
        
        # 파일이 없거나 기타 조건이 맞지 않으면 캐시가 유효하지 않으므로 False를 반환합니다.
        print("[DEBUG] 캐시 파일이 없거나 기타 조건이 맞지 않음.")
        return False

