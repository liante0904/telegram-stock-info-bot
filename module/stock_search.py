import requests
import argparse

def search_stock(query):
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
            'code': item['code']
        }
        for item in data['items']
        if  item['typeCode'] in ['KOSPI', 'KOSDAQ']
        and not (40000 <= int(item['code'][0:5]) <= 49999 and '스팩' in item['name'])
    ]
    print(filtered_items)
    return filtered_items



def main():
    parser = argparse.ArgumentParser(description="업종명에 따른 종목 정보를 크롤링합니다.")
    parser.add_argument('query', type=str, nargs='?', help='업종명을 입력하세요.')
    parser.add_argument('option', type=str, nargs='?', help='옵션: 퀀트 정보를 가져오려면 "퀀트"를 입력하세요.')
    args = parser.parse_args()
    search_stock('PLUS K방산')
    


if __name__ == '__main__':
    main()
