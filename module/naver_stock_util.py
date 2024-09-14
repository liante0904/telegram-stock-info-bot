from datetime import datetime, time
import pytz
import requests
import sys
import os
# 현재 스크립트의 상위 디렉터리를 모듈 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sql.kr_isu import select_data as select_sqlite_kr_stock

def check_market_status(market):
    """한국 시간대를 기준으로 요일을 판단한 후, 시장 상태를 결정합니다."""
    
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    day_of_week = now.weekday()  # 0: 월요일, 1: 화요일, ..., 6: 일요일
    month = now.month            # 현재 월
    current_time = now.time()    # 현재 시간

    # 시간 범위 정의
    close_start_time = time(16, 30)  # 오후 16:30
    close_end_time = time(8, 0)      # 오전 08:00

    # 토요일(5) 또는 일요일(6)인 경우
    if day_of_week in [5, 6]:
        return 'CLOSE'
    
    # 16:30부터 08:00까지의 시간 범위 확인
    # 수능 등 기타 이유로 정규장을 16:30 까지 API로 체크
    if (current_time >= close_start_time) or (day_of_week == 0 and current_time < close_end_time):
        return 'CLOSE'

    # 주중의 경우, API를 통해 시장 상태 확인
    api_url = f'https://m.stock.naver.com/api/index/{market}/basic'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        api_response = requests.get(api_url, headers=headers)
        if api_response.status_code == 200:
            stock_basic_data = api_response.json()
            return stock_basic_data.get('marketStatus', 'UNKNOWN')  # API 응답에서 'marketStatus' 키를 찾아 반환
        else:
            return 'UNKNOWN'  # API 요청 실패 시 'UNKNOWN'
    except Exception as e:
        print(f"Error fetching API data: {e}")
        return 'UNKNOWN'


def search_stock_code(query):
    url = 'https://ac.stock.naver.com/ac'
    params = {
        'q': query,
        'target': 'index,stock,marketindicator'
    }

    response = requests.get(url, params=params)
    data = response.json()
    print(data)
    
    # query가 6자리이고 첫 5자리가 모두 숫자인지 확인하는 함수
    def is_query_numeric(query):
        return len(query) == 6 and query[:5].isdigit()
    
    # query를 소문자로 변환하여 비교
    query_lower = query.lower()
        
    # 데이터 항목이 1건이면 필터링 없이 바로 반환
    if len(data['items']) == 1:
        # 반환할 항목을 추출하여 리스트로 포장
        item = data['items'][0]
        result = [{
            'name': item['name'],
            'code': item['code'],
            'typeCode': item['typeCode'],
            'typeName': item['typeName'],
            'url': item['url'],
            'reutersCode': item['reutersCode'],
            'nationCode': item['nationCode'],
            'nationName': item['nationName']
        }]
        print(result)
        return result

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
        if (item['name'].strip() == str(query).strip() or item['code'] == str(query).strip())
    ]

    # 추가 조건을 적용하여 최종 필터링
    final_filtered_items = [
        item for item in filtered_items
        if item['nationCode'] != 'KOR' or (
            not (40000 <= int(item['code'][0:5]) <= 49999) and 
            '스팩' not in item['name']
        )
    ]

    print(final_filtered_items)
    return final_filtered_items

def search_stock_code_mobileAPI(query):
    # 1-1. select_sqlite_kr_stock을 통해 데이터를 조회
    result = select_sqlite_kr_stock(isu=query)
    
    # 1-1. 조회된 값이 있으면 바로 반환
    if result:  # 빈값인 경우 [] 반환이므로 그대로 사용 가능
        print("SQLite 조회 결과:", result)
        
        # ISU_NO와 ISU_NM을 'code'와 'name'으로 변환하고 나머지 데이터도 포함하여 반환
        transformed_result = [
            {
                'code': item['ISU_NO'],       # ISU_NO -> code
                'name': item['ISU_NM'],       # ISU_NM -> name
                'market': item['MARKET'],     # MARKET 포함
                'sector': item['SECTOR'],     # SECTOR 포함
                'last_updated': item['LAST_UPDATED']  # LAST_UPDATED 포함
            }
            for item in result
        ]
        
        print("변환된 결과:", transformed_result)
        return transformed_result
    else:
        # 1-2. 빈 값을 리턴받으면 해외 주식으로 간주
        print("해외 주식으로 간주하고 네이버 API로 검색합니다.")
        
        # 네이버 API를 통한 해외 주식 조회 로직
        url = 'https://m.stock.naver.com/front-api/search/autoComplete'
        params = {
            'query': query,
            'target': 'stock,index,marketindicator'
        }

        response = requests.get(url, params=params)
        data = response.json()
        print(data)
        
        
        
        # 데이터 항목이 1건이면 필터링 없이 바로 반환
        if len(data['result']['items'])  > 0:
            return data['result']['items']
        else:
            return []

def main():
    r = search_stock_code_mobileAPI('aapl')
    if r:
        print('0===>', r)
        
    else:
        print('No results found.')

if __name__ == '__main__':
    main()
