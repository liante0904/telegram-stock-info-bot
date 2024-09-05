import requests
import sys
import os
# 현재 스크립트의 상위 디렉터리를 모듈 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sql.kr_isu import select_data as select_sqlite_kr_stock

def search_stock(query):
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
            'code': item['code']
        }]
        print(result)
        return result

    # 필터링된 결과를 저장할 리스트
    filtered_items = [
        {
            'name': item['name'],
            'code': item['code']
        }
        for item in data['items']
        if item['typeCode'] in ['KOSPI', 'KOSDAQ']
        and not (40000 <= int(item['code'][0:5]) <= 49999 and '스팩' in item['name'])
        and (item['code'] == query if is_query_numeric(query) else item['name'].lower() == query_lower) # 종목명 혹은 종목코드 필터링
    ]
    print(filtered_items)
    return filtered_items

def search_stock_all(query):
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
    r = search_stock_all('aapl')
    if r:
        print('0===>', r)
    else:
        print('No results found.')

if __name__ == '__main__':
    main()
