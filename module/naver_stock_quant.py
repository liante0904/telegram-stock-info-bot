import requests
import json
from datetime import datetime, timedelta

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


def fetch_dividend_total_stock_count():
    base_url = "https://m.stock.naver.com/api/stocks/dividend/rate"
    params = {
        'page': 1,
        'pageSize': 2  # 이해를 위해 pageSize는 2로 설정
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        total_count = data.get('totalCount', 0)
        return total_count
    else:
        print("Total count를 가져오는 데 실패했습니다.")
        return 0

def fetch_dividend_data(total_count, page_size=100):
    base_url = "https://m.stock.naver.com/api/stocks/dividend/rate"
    dividends = []
    page = 1

    while (page - 1) * page_size < total_count:
        params = {
            'page': page,
            'pageSize': page_size
        }
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            dividends.extend(data.get('dividends', []))
            print(f"페이지 {page}에서 {len(data.get('dividends', []))}개의 데이터를 가져왔습니다.")
        else:
            print(f"페이지 {page}를 가져오는 데 실패했습니다.")
            break
        
        page += 1
    
    return dividends


def main():
    fetch_stock_yield_by_period('005930')

if __name__ == '__main__':
    main()

