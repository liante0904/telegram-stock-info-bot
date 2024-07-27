import argparse
import requests
from bs4 import BeautifulSoup

# 업종 페이지 URL (업종별 링크는 상대 경로로 제공됩니다)
base_upjong_url = 'https://finance.naver.com/sise/sise_group.naver?type=upjong'

# HTTP 헤더 설정
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_upjong_list():
    # 웹 페이지 요청
    response = requests.get(base_upjong_url, headers=headers)
    response.encoding = 'euc-kr'  # Naver 페이지는 EUC-KR 인코딩을 사용합니다.

    # 페이지 내용 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 업종명과 링크를 찾기 위한 데이터 추출
    table = soup.find('table', {'class': 'type_1'})
    if not table:
        raise ValueError("업종 목록 테이블을 찾을 수 없습니다.")
    
    rows = table.find_all('tr')[2:]  # 헤더를 제외하고 데이터만 가져옵니다.

    # 데이터 수집
    data = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:  # 필요한 만큼의 데이터가 있는지 확인
            업종명 = cols[0].get_text(strip=True)
            등락률 = cols[1].get_text(strip=True)
            링크 = cols[0].find('a')['href']
            data.append((업종명, 등락률, 링크))
    
    return data

def fetch_stock_info(upjong_link):
    base_url = 'https://finance.naver.com'
    full_url = base_url + upjong_link
    print(f'Fetching stock info from: {full_url}')  # Debugging message

    # 웹 페이지 요청
    response = requests.get(full_url, headers=headers)
    response.encoding = 'euc-kr'
    soup = BeautifulSoup(response.text, 'html.parser')

    # 종목 정보를 포함하는 테이블을 찾기
    table = soup.find('table', {'class': 'type_5'})  # 'type_5' 클래스가 사용됨
    if not table:
        raise ValueError(f'종목 정보를 찾을 수 없습니다: {full_url}')
    
    rows = table.find_all('tr')[1:]  # 헤더를 제외하고 데이터만 가져옵니다.

    # 데이터 수집
    stock_data = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 10:  # 필요한 만큼의 데이터가 있는지 확인
            종목명 = cols[0].get_text(strip=True)
            현재가 = cols[1].get_text(strip=True)
            전일비_raw = cols[2].get_text(strip=True)
            등락률 = cols[3].get_text(strip=True)

            # 전일비에 '+'와 '-' 추가
            if '상승' in 전일비_raw:
                전일비 = '+' + 전일비_raw.replace('상승', '').strip()
            elif '하락' in 전일비_raw:
                전일비 = '-' + 전일비_raw.replace('하락', '').strip()
            else:
                전일비 = 전일비_raw  # 기본적으로 변환되지 않는 경우 원래 값 유지

            stock_data.append((종목명, 현재가, 전일비, 등락률))
    
    return stock_data

def main():
    parser = argparse.ArgumentParser(description="업종명에 따른 종목 정보를 크롤링합니다.")
    parser.add_argument('upjong_name', type=str, nargs='?', help='업종명을 입력하세요.')
    args = parser.parse_args()
    
    upjong_list = fetch_upjong_list()
    
    if args.upjong_name:
        # 업종명을 입력받은 경우
        upjong_map = {업종명: (등락률, 링크) for 업종명, 등락률, 링크 in upjong_list}
        if args.upjong_name in upjong_map:
            등락률, 링크 = upjong_map[args.upjong_name]
            stock_info = fetch_stock_info(링크)
            if stock_info:
                print(f'\n업종명: {args.upjong_name}')
                print(f"{'종목명':<20} {'현재가':<10} {'전일비':<10} {'등락률':<10}")
                for 종목명, 현재가, 전일비, 등락률 in stock_info:
                    print(f"{종목명:<20} {현재가:<10} {전일비:<10} {등락률:<10}")
            else:
                print("종목 정보를 가져오는 데 문제가 발생했습니다.")
        else:
            print("입력한 업종명이 올바르지 않습니다.")
    else:
        # 업종명을 입력받지 않은 경우
        print("업종 목록:")
        for 업종명, 등락률, _ in upjong_list:
            print(f'업종명: {업종명}, 등락률: {등락률}')

if __name__ == '__main__':
    main()
