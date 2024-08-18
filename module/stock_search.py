import requests

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

def main():
    r = search_stock('cj')
    if r:
        print('0===>', r[0])
    else:
        print('No results found.')

if __name__ == '__main__':
    main()
