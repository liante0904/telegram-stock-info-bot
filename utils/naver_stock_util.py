import requests
import os
import sys
import math
from datetime import datetime, timedelta, time
import pytz
# 현재 스크립트의 상위 디렉터리를 모듈 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# 전역 변수로 업종 코드-업종명 매핑 딕셔너리 선언
industry_code_name_map = None

def get_industry_name(industry_code):
    """
    업종 코드를 입력하면 업종명을 반환.
    최초 호출 시에만 API를 통해 데이터를 로딩.
    """
    global industry_code_name_map
    

    def load_industry_code_name_map():
        """
        네이버 API에서 업종 목록을 받아와 코드-업종명 매핑 딕셔너리를 생성.
        """
        global industry_code_name_map
        if industry_code_name_map is not None:
            return  # 이미 로딩된 경우 재호출 방지

        url = "https://m.stock.naver.com/api/stocks/industry?page=1&pageSize=100"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()

        # 코드-업종명 매핑 생성
        industry_code_name_map = {}
        for group in data['groups']:
            code = str(group['no'])
            name = group['name']
            industry_code_name_map[code] = name

    
    if industry_code_name_map is None:
        load_industry_code_name_map()
    return industry_code_name_map.get(str(industry_code), "알 수 없음")

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

    # 조회 기간을 380일로 설정 (1년 데이터 확보 보장)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=380)
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')

    trend_url = f'https://api.stock.naver.com/chart/domestic/item/{stock_code}/day?startDateTime={start_date_str}0000&endDateTime={end_date_str}0000'
    print(f"[DEBUG] Fetching data from {trend_url}")
    trend_data = fetch_data(trend_url)

    if not trend_data:
        return {}
    
    # 현재 데이터가 없는 경우 가장 최신 데이터로 대체
    current_price = None
    for item in reversed(trend_data):  # 최신 데이터부터 탐색
        if 'closePrice' in item:
            current_price = int(item['closePrice'])
            break

    if current_price is None:
        print("[ERROR] No valid current price found in data.")
        return {"error": "No valid current price found"}

    # 가격 데이터를 날짜별로 정리
    prices = {item['localDate']: int(item['closePrice']) for item in trend_data}

    def calculate_return(past_price):
        if past_price is not None:
            percentage_change = round((current_price / past_price - 1) * 100, 2)
            return "{:.2f}".format(percentage_change)
        return "N/A"

    timeframes = {
        '1D': 1,
        '1W': 7,
        '1M': 30,
        '3M': 90,
        '6M': 180,
        'YTD': 0,  # YTD는 별도로 처리
        '1Y': 365
    }

    returns = {}
    for key, days in timeframes.items():
        past_price = None

        if key == 'YTD':
            # 현재 연도 시작일 (1월 1일 기준)
            current_year_start = datetime(end_date.year, 1, 1)
            current_year_start_str = current_year_start.strftime('%Y%m%d')

            # 현재 연도 1월의 가장 빠른 일자 데이터 찾기
            for date_str in sorted(prices.keys()):
                if date_str.startswith(str(end_date.year)) and int(date_str[4:6]) == 1:
                    past_price = prices[date_str]
                    break

            # 현재 연도 1월 데이터가 없는 경우 1월 1일 이전의 가장 가까운 데이터 사용
            if not past_price:
                for date_str in sorted(prices.keys(), reverse=True):
                    if date_str < current_year_start_str:
                        past_price = prices[date_str]
                        break

        elif key == '1Y':
            # 1년 전 날짜의 데이터 확보 (1년 이상 넉넉한 범위 탐색)
            target_date = end_date - timedelta(days=days)
            target_date_str = target_date.strftime('%Y%m%d')

            for date_str in sorted(prices.keys(), reverse=True):
                if date_str <= target_date_str:
                    past_price = prices.get(date_str)
                    break

            # 1Y 데이터가 없는 경우 더 과거 데이터를 사용
            if not past_price:
                for date_str in sorted(prices.keys(), reverse=True):
                    if int(date_str) < int(target_date_str):
                        past_price = prices[date_str]
                        break

        else:
            # 일반적인 기간에 대한 과거 데이터 탐색
            target_date = end_date - timedelta(days=days)
            target_date_str = target_date.strftime('%Y%m%d')

            for date_str in sorted(prices.keys(), reverse=True):
                if date_str <= target_date_str:
                    past_price = prices.get(date_str)
                    break

        # 과거 가격이 없는 경우 최근 데이터를 사용
        if not past_price:
            for offset in range(1, 8):  # 7일 이전까지 탐색
                adjusted_date = end_date - timedelta(days=offset)
                adjusted_date_str = adjusted_date.strftime('%Y%m%d')
                if adjusted_date_str in prices:
                    past_price = prices[adjusted_date_str]
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
    r = stock_fetch_yield_by_period('005930')
    print(r)
    
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