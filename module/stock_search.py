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
    # 종목코드로 필터링
    def is_query_numeric(query):
        return len(query) == 6 and query[:5].isdigit()
    
    # 필터링된 결과를 저장할 리스트
    filtered_items = [
        {
            'name': item['name'],
            'code': item['code']
        }
        for item in data['items']
        if item['typeCode'] in ['KOSPI', 'KOSDAQ']
        and not (40000 <= int(item['code'][0:5]) <= 49999 and '스팩' in item['name'])
        and (item['code'] == query if is_query_numeric(query) else item['name'] == query) # 종목명 혹은 종목코드 필터링
    ]
    print(filtered_items)
    return filtered_items




def main():
    r= search_stock('005935')
    print('0===>',r[0])

if __name__ == '__main__':
    main()