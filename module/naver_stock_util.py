import requests
import os
import sys
import math
from datetime import datetime, timedelta, time
import pytz
# 현재 스크립트의 상위 디렉터리를 모듈 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_market_status(nation_code):
    """주어진 nation_code에 따라 API를 통해 시장 상태와 마지막 거래일을 확인하여 시장 상태를 결정합니다."""
    
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)

    # nation_code에 따른 API URL 정의
    if nation_code == 'KOR':
        api_url = 'https://m.stock.naver.com/api/index/KOSPI/basic'  # 한국 시장
    else:
        api_url = f'https://api.stock.naver.com/index/nation/{nation_code}'  # 해외 시장

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        api_response = requests.get(api_url, headers=headers)
        if api_response.status_code == 200:
            stock_basic_data = api_response.json()

            # 한국 시장 데이터 처리
            if nation_code == 'KOR':
                market_status = stock_basic_data.get('marketStatus', 'UNKNOWN')
                local_traded_at = stock_basic_data.get('localTradedAt')
            
            # 해외 시장 데이터 처리 (첫 번째 거래소 정보 기준)
            else:
                first_exchange_data = stock_basic_data[0]  # 가장 첫 번째 거래소 데이터를 사용
                market_status = first_exchange_data.get('marketStatus', 'UNKNOWN')
                local_traded_at = first_exchange_data.get('localTradedAt')

            # localTradedAt 값이 존재하는 경우 처리
            if local_traded_at:
                # ISO 형식에서 타임존 제외 후 변환
                last_traded_datetime = datetime.fromisoformat(local_traded_at[:-6])
                print(f"[DEBUG] 마지막 거래일: {last_traded_datetime}")

                # 현재 시간이 마지막 거래일보다 나중인지 확인하여 장이 휴장인지 판단
                if last_traded_datetime.date() < now.date():
                    print("[DEBUG] 장이 휴장입니다.")
                    return 'CLOSE', last_traded_datetime  # 두 개의 값 반환

            return market_status, last_traded_datetime  # 두 개의 값 반환

        else:
            return 'UNKNOWN', None  # API 요청 실패 시 두 개의 값 반환

    except Exception as e:
        print(f"Error fetching API data: {e}")
        return 'UNKNOWN', None  # 예외 처리 시 두 개의 값 반환

def stock_fetch_yield_by_period(stock_code=None, date=None):
    # stock_code가 제공되지 않았을 때 에러 처리
    if not stock_code:
        print("Error: stock_code is required but was not provided.")
        return {"error": "stock_code is required"}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def fetch_data(url):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data: Status code {response.status_code}")
            return None

    # 1년간 가격 데이터를 가져오기
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1년 전 날짜
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')

    trend_url = f'https://api.stock.naver.com/chart/domestic/item/{stock_code}/day?startDateTime={start_date_str}0000&endDateTime={end_date_str}0000'
    trend_data = fetch_data(trend_url)

    if not trend_data:
        return {}
    
    # print(trend_data)

    # 현재 가격을 trend_data의 마지막 데이터에서 가져오기
    current_price = int(trend_data[-1]['closePrice'])

    # 가격 데이터를 날짜별로 정리
    prices = {item['localDate']: int(item['closePrice']) for item in trend_data}

    # 수익률 계산
    def calculate_return(past_price):
        if past_price is not None:
            percentage_change = round((current_price / past_price - 1) * 100, 2)
            return "{:.2f}".format(percentage_change)
        return "N/A"

    # 1D, 1W, 1M, 3M, 6M, YTD, 1Y 수익률 계산
    timeframes = {
        '1D': 1,
        '1W': 7,
        '1M': 30,
        '3M': 90,
        '6M': 180,
        'YTD': (datetime.now() - datetime(datetime.now().year, 1, 1)).days,
        '1Y': 365
    }

    returns = {}
    end_date = datetime.now()
    
    for key, days in timeframes.items():
        target_date = end_date - timedelta(days=days)
        target_date_str = target_date.strftime('%Y%m%d')
        past_price = None
        
        for date_str in sorted(prices.keys(), reverse=True):
            if date_str <= target_date_str:
                past_price = prices.get(date_str)
                break
        
        returns[key] = calculate_return(past_price)

    return returns

def search_stock_code(query):
    url = 'https://ac.stock.naver.com/ac'
    params = {
        'q': query,
        'target': 'index,stock,marketindicator'
    }

    response = requests.get(url, params=params)
    data = response.json()
    print(data)
    
    # 필터링된 결과를 저장할 리스트
    filtered_items = [
        {
            'name': item['name'],
            'code': item['code'],
            'typeCode': item['typeCode'],
            'typeName': item['typeName'],
            'url': item['url'],
            'reutersCode': item['reutersCode'],
            'nationCode': item['nationCode'],
            'nationName': item['nationName']
        }
        for item in data['items']
        if (item['name'].strip().lower() == str(query).strip().lower() or item['code'].lower() == str(query).strip().lower())
    ]
    
    # `query`와 일치하는 항목이 있을 경우 해당 항목 반환
    if filtered_items:
        print(filtered_items)
        return filtered_items
    
    # `query`와 일치하는 항목이 없는 경우, 스팩주를 제거한 나머지 항목 반환
    non_spec_items = []
    for item in data['items']:
        if item['nationCode'] != 'KOR':
            non_spec_items.append({
                'name': item['name'],
                'code': item['code'],
                'typeCode': item['typeCode'],
                'typeName': item['typeName'],
                'url': item['url'],
                'reutersCode': item['reutersCode'],
                'nationCode': item['nationCode'],
                'nationName': item['nationName']
            })
        else:
            # `nationCode`가 'KOR'인 경우 추가 조건 적용
            if not (40000 <= int(item['code'][0:5]) <= 49999) and '스팩' not in item['name']:
                non_spec_items.append({
                    'name': item['name'],
                    'code': item['code'],
                    'typeCode': item['typeCode'],
                    'typeName': item['typeName'],
                    'url': item['url'],
                    'reutersCode': item['reutersCode'],
                    'nationCode': item['nationCode'],
                    'nationName': item['nationName']
                })
    
    print(non_spec_items)
    return non_spec_items

def calculate_page_count(requested_count: int, page_size: int = 100) -> int:
    """
    페이지 수를 계산하는 함수.
    
    :param requested_count: 요청된 종목 수
    :param page_size: 한 페이지당 종목 수 (기본값: 100)
    :return: 필요한 페이지 수
    """
    if requested_count <= 0:
        raise ValueError("요청 수는 양수여야 합니다.")
    
    # 페이지 수 계산 (ceil 사용하여 올림 처리)
    return math.ceil(requested_count / page_size)

def main():
    # r = search_stock_code_mobileAPI('이토추')
    # r = search_stock_code('이토추')
    # r = fetch_stock_yield_by_period(stock_code='188260')
    r = check_market_status('JPN')
    if r:
        print('0===>', r)
        
    else:
        print('No results found.')

if __name__ == '__main__':
    main()