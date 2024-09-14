import requests
import os
import sys
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.cache_manager import CacheManager

def fetch_stock_yield_by_period(stock_code=None, date=None):
    # stock_code가 제공되지 않았을 때 에러 처리
    if not stock_code:
        print("Error: stock_code is required but was not provided.")
        return {"error": "stock_code is required"}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def fetch_data(url):
        # print(f"Fetching data from: {url}")  # Debugging message
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data: Status code {response.status_code}")
            return None

    # 현재 가격 가져오기
    basic_info_url = f'https://m.stock.naver.com/api/stock/{stock_code}/basic'
    basic_data = fetch_data(basic_info_url)

    if not basic_data:
        return {}

    current_price = int(basic_data['closePrice'].replace(',', ''))

    # 날짜별 가격 가져오기
    def fetch_past_price(days_ago):
        past_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y%m%d')
        original_date = datetime.strptime(past_date, '%Y%m%d')
        one_week_ago = original_date - timedelta(weeks=1)

        while True:
            trend_url = f'https://api.stock.naver.com/chart/domestic/item/{stock_code}/day?startDateTime={past_date}0000&endDateTime={past_date}0000'
            trend_data = fetch_data(trend_url)
            
            if trend_data and len(trend_data) > 0:
                return int(trend_data[0]['closePrice'])
            
            # 날짜를 하루 전으로 이동
            original_date -= timedelta(days=1)
            past_date = original_date.strftime('%Y%m%d')
            
            # 일주일 이내로 제한
            if original_date < one_week_ago:
                break
        
        return None


    # 수익률 계산
    def calculate_return(past_price):
        if past_price is not None:
            percentage_change = round((current_price / past_price - 1) * 100, 2)
            return "{:.2f}".format(percentage_change)
        return None

    # 1D, 1M, 6M, YTD, 1Y 수익률 계산
    timeframes = {
        '1D': 1,
        '1W': 7,
        '1M': 30,
        '3M': 90,        
        '6M': 180,
        'YTD': (datetime.now() - datetime(datetime.now().year, 1, 1)).days,
        '1Y': 365
    }

    returns = {key: calculate_return(fetch_past_price(days)) for key, days in timeframes.items()}

    return returns

def fetch_dividend_stock_list_API(page=1, pageSize=100):
    # CacheManager 인스턴스 생성
    cache_manager = CacheManager("cache", "dividend_stock")

    # 캐시 키를 페이지별로 구분하여 설정
    cache_key = f'dividend_stock_{page}'

    # 캐시가 유효한지 확인
    if cache_manager.is_cache_valid(cache_key):
        print(f"[DEBUG] 유효한 캐시를 발견했습니다. (Page {page})")
        return cache_manager.load_cache(cache_key)

    print(f"[DEBUG] 유효한 캐시가 없으므로 API를 호출합니다. (Page {page})")
    # API 호출 URL
    url = f"https://m.stock.naver.com/api/stocks/dividend/rate?page={page}&pageSize={pageSize}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"API 요청 실패: {response.status_code}")

    data = response.json()

    # 데이터를 캐시에 저장 (페이지별로 구분)
    cache_manager.save_cache(cache_key, data)

    return data

def main():
    fetch_stock_yield_by_period('005930')

if __name__ == '__main__':
    main()

