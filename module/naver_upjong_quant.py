import argparse
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd  # pandas를 추가합니다
from module.cache_manager import CacheManager

from datetime import datetime
from module.naver_stock_quant import fetch_stock_yield_by_period


CACHE_FILE = "upjong_cache.json"
MARKET_OPEN_TIME = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
MARKET_CLOSE_TIME = datetime.now().replace(hour=15, minute=30, second=0, microsecond=0)

cache_manager = CacheManager(CACHE_FILE, MARKET_OPEN_TIME, MARKET_CLOSE_TIME)


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
    print(data)
    return data

def fetch_upjong_list_API():
    if cache_manager.is_cache_valid():
        print("[DEBUG] 유효한 캐시를 발견했습니다.")
        return cache_manager.get_cached_data()
    
    print("[DEBUG] 유효한 캐시가 없으므로 API를 호출합니다.")
    url = "https://m.stock.naver.com/api/stocks/industry?pageSize=100"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"API 요청 실패: {response.status_code}")
    
    data = response.json()
    
    result = []
    for group in data['groups']:
        name = group['name']
        change_rate = f"{group['changeRate']}%"
        link = f"/sise/sise_group_detail.naver?type=upjong&no={group['no']}"
        result.append((name, change_rate, link))
    
    if data['marketStatus'] == 'CLOSE':
        print("[DEBUG] 마켓이 원래 개장 중이어야 하지만, 현재는 CLOSE 상태입니다 (휴장일 가능성).")
        cache_manager.save_cache({'result': result, 'marketStatus': 'CLOSE'})
    
    return result

def fetch_stock_info_in_upjong(upjong_link):
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

            # 종목 링크 추출
            link_tag = cols[0].find('a')
            if link_tag and 'href' in link_tag.attrs:
                link = base_url + link_tag['href']
            else:
                link = 'N/A'  # 링크가 없는 경우 'N/A'로 처리

            stock_data.append((종목명, 현재가, 전일비, 등락률, link))
    
    return stock_data

def fetch_stock_info_quant(stock_code):
    url = f'https://finance.naver.com/item/main.naver?code={stock_code}'
    
    print(f"Fetching data from: {url}")  # Debugging message
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # HTTP 요청
    response = requests.get(url, headers=headers)
    response.encoding = 'euc-kr'
    
    if response.status_code == 200:
        print("Page successfully fetched.")  # Debugging message
    else:
        print(f"Failed to fetch page: Status code {response.status_code}")
        return {}

    # 페이지 내용 파싱
    soup = BeautifulSoup(response.text, 'html.parser')


    # #middle > dl 선택자를 사용하여 요소 찾기
    dl_tag = soup.select_one('#middle > dl')

    # 키-값을 저장할 딕셔너리 생성
    base_data = {}

    # 모든 <dd> 태그를 찾아 처리
    dd_tags = dl_tag.find_all('dd')

    for i, dd in enumerate(dd_tags):
        text = dd.text.strip()
        
        if i == 0:  # 첫 번째 <dd>는 그대로 저장
            base_data[f'entry_{i+1}'] = text
        else:  # 나머지는 키-값으로 저장
            if ' ' in text:
                key, value = text.split(' ', 1)
            else:
                key, value = text, ''
            
            # "현재가" 항목에 대한 특수 처리
            if key == "현재가":
                # 현재가 값을 75,600까지만 저장
                base_data[key] = value.split(' ')[0]
                
                # "전일대비" 및 나머지 값을 추출하여 새로운 키로 추가
                # '전일대비'라는 문자열 기준으로 split
                parts = value.split('전일대비')
                if len(parts) > 1:
                    comparison_value = parts[1].strip()
                    
                    # 숫자만 추출 (하락/상승 등의 텍스트는 제거)
                    numeric_value = re.findall(r'-?\d+', comparison_value)
                    if numeric_value:
                        base_data['전일비'] = " ".join(numeric_value)  # 숫자만 저장
                    
                    # 등락률 추출
                    percent_match = re.search(r'(-?\d+\.\d+)\s+퍼센트', comparison_value)
                    if percent_match:
                        base_data['등락률'] = percent_match.group(1)
            else:
                base_data[key] = value

    # 결과 출력
    for key, value in base_data.items():
        print(f"{key} : {value}")


    # # 종목명 추출
    # stock_name_tag = soup.select_one('#middle > dl > dd:nth-child(3)')
    # if stock_name_tag:
    #     stock_name = stock_name_tag.get_text(strip=True).split('종목명 ')[1]  # 종목명만 추출
    # else:
    #     stock_name = 'N/A'
    #     print("종목명을 찾을 수 없습니다.")  # 로그: 종목명 없음

    # PER, 추정PER, PBR, 배당수익률 정보를 담고 있는 테이블 찾기
    info_section = soup.select_one('#tab_con1 > div:nth-child(5)')
    if not info_section:
        print("정보 섹션을 찾을 수 없습니다.")
        return

    print("Information section found.")  # 로그: 정보 섹션 찾음

    # 각 항목에 대한 CSS 선택자
    data = {
        '종목명': base_data.get('종목명', 'N/A'),
        '현재가': base_data.get('현재가', 'N/A').replace(',', ''),
        '전일비': base_data.get('전일비', 'N/A').replace(',', ''),
        '등락률': base_data.get('등락률', 'N/A')
    }
    
    try:
        # 현재주가
        current_price_tag = soup.select_one('#middle > dl > dd:nth-child(5)')
        current_price_text = current_price_tag.get_text(strip=True) if current_price_tag else 'N/A'

        # 현재가, 전일비, 등락률 추출
        pattern = re.compile(r'''
            현재가\s+([\d,]+)\s+          # 현재가 (숫자와 쉼표)
            전일대비\s+                  # 전일대비 (문자열)
            (상승|하락)\s+                # 상승 또는 하락
            ([\d,]+)\s+                  # 전일비 (숫자와 쉼표)
            (플러스|마이너스)?\s*        # 플러스 또는 마이너스 (선택적)
            ([\d.]+)\s+퍼센트            # 등락률 (숫자)
        ''', re.VERBOSE)

        match = pattern.search(current_price_text)
        if match:
            data['현재가'] = int(match.group(1).replace(',', ''))
            change_amount = int(match.group(3).replace(',', ''))
            change_percent = match.group(4)
            if match.group(2) == '하락':
                change_percent = '-' + match.group(5)
                change_amount  = '-' + str(change_amount)
            else:
                change_percent = match.group(5)
                change_amount  = change_amount
            data['전일비'] = change_amount
            data['등락률'] = change_percent
        else:
            data['전일비'] = 'N/A'
            data['등락률'] = 'N/A'
            print('현재가, 전일비, 등락률을 찾을 수 없습니다.')

        # PER
        per_value = info_section.select_one('tr:nth-of-type(1) > td')
        if per_value:
            data['PER'] = per_value.get_text(strip=True).split('l')[0].split('배')[0]
        else:
            data['PER'] = 'N/A'
            print("PER 값을 찾을 수 없습니다.")  # 로그: PER 없음

        # 추정PER
        est_eps_value = soup.select_one('#_cns_eps')
        if est_eps_value:
            est_eps_text = est_eps_value.get_text(strip=True).split('|')[0]
            try:
                est_eps_value = float(est_eps_text.replace(',', ''))
                if data['현재가'] > 0:
                    fwd_per = round(data['현재가'] / est_eps_value, 2)
                    data['fwdPER'] = fwd_per
                else:
                    data['fwdPER'] = 'N/A'
                    print("현재 주식 가격이 유효하지 않습니다.")
            except ValueError:
                data['fwdPER'] = 'N/A'
                print("FWD EPS 값이 유효하지 않습니다.")
        else:
            data['fwdPER'] = 'N/A'
            print("FWD EPS 값을 찾을 수 없습니다.")

        # PBR
        pbr_value = info_section.select_one('tr:nth-of-type(2) > td')
        if pbr_value:
            data['PBR'] = pbr_value.get_text(strip=True).split('l')[0].split('배')[0]
        else:
            data['PBR'] = 'N/A'
            print("PBR 값을 찾을 수 없습니다.")  # 로그: PBR 없음

        # 배당수익률
        dividend_yield_value = info_section.select_one('#_dvr')
        if dividend_yield_value:
            data['배당수익률'] = dividend_yield_value.get_text(strip=True).split(' ')[0]
        else:
            data['배당수익률'] = 'N/A'
            print("배당수익률 값을 찾을 수 없습니다.")  # 로그: 배당수익률 없음

        # 예상 배당수익률
        est_dividend_price_value_text = soup.select_one('#content > div.section.cop_analysis > div.sub_section > table > tbody > tr:nth-child(14) > td.t_line.cell_strong')
        if est_dividend_price_value_text:
            est_dividend_price_value_text = est_dividend_price_value_text.get_text(strip=True).split('%')[0]
            est_dividend_price_value_text = est_dividend_price_value_text.replace(',', '')
            try:
                est_dividend_price_value = int(est_dividend_price_value_text)
            except ValueError:
                est_dividend_price_value = None
        else:
            est_dividend_price_value = None

        if est_dividend_price_value is not None and est_dividend_price_value != 0:
            est_dividend_yield_value = est_dividend_price_value / data['현재가'] * 100
            est_dividend_yield_value = round(est_dividend_yield_value, 2)
        else:
            est_dividend_yield_value = 'N/A'

        if est_dividend_yield_value:
            data['예상배당수익률'] = est_dividend_yield_value
        else:
            data['예상배당수익률'] = 'N/A'
            print("예상배당수익률 값을 찾을 수 없습니다.")  # 로그: 예상 배당수익률 없음

        # ROE 정보 추출
        roe_tag = soup.select_one('#content > div.section.cop_analysis > div.sub_section > table > tbody > tr:nth-child(6) > td.t_line.cell_strong')
        if roe_tag:
            data['ROE'] = roe_tag.get_text(strip=True).replace('\n', 'N/A').replace('\xa0', 'N/A').strip()
        else:
            data['ROE'] = 'N/A'
            print("ROE 정보를 찾을 수 없습니다.")  # 로그: ROE 정보 없음

        # 종목코드
        data['url'] = url

        # 네이버 주소 
        data['stock_code'] = stock_code

    except Exception as e:
        print(f"Error parsing data: {e}")  # 로그: 파싱 오류

    print(url)

    # 네이버 주소 
    data['네이버url'] = url
    print(stock_code)

    # 종목코드
    data['종목코드'] = str(stock_code)

    # 기간 수익률

    # 문자열을 안전하게 딕셔너리로 변환
    yield_data_dict = fetch_stock_yield_by_period(stock_code=stock_code)

    # 각 키와 값을 data 딕셔너리에 추가
    for key, value in yield_data_dict.items():
        data[key] = value
 


    # 숫자로 변환할 수 있는 항목들을 float으로 변환
    # 숫자로 변환할 수 있는 키들을 나열합니다 (종목코드를 제외)
    numeric_keys = ['PER', 'PBR', '배당수익률', 'ROE', '현재가', '전일비', '등락률', '1D', '1W', '1M', '3M', '6M', 'YTD', '1Y']

    for key in numeric_keys:
        if key in data and isinstance(data[key], str):
            # 문자열에서 ','와 '%' 제거 후 float으로 변환
            value = data[key].replace(',', '').replace('%', '')
            try:
                data[key] = float(value)
            except ValueError:
                data[key] = 'N/A'  # 변환할 수 없는 경우 'N/A'로 처리

    # 순서 지정된 컬럼 순서에 맞게 데이터 정렬
    ordered_data = {
        '종목명': data.get('종목명', 'N/A'),
        'PER': data.get('PER', 'N/A'),
        'fwdPER': data.get('fwdPER', 'N/A'),
        'PBR': data.get('PBR', 'N/A'),
        '배당수익률': data.get('배당수익률', 'N/A'),
        '예상배당수익률': data.get('예상배당수익률', 'N/A'),
        'ROE': data.get('ROE', 'N/A'),
        '현재가': data.get('현재가', 'N/A'),
        '전일비': data.get('전일비', 'N/A'),
        '등락률': data.get('등락률', 'N/A'),
        '비고(메모)': data.get('비고(메모)', ' '),
        '1D': data.get('1D', 'N/A'),
        '1W': data.get('1W', 'N/A'),
        '1M': data.get('1M', 'N/A'),
        '3M': data.get('3M', 'N/A'),
        '6M': data.get('6M', 'N/A'),
        'YTD': data.get('YTD', 'N/A'),
        '1Y': data.get('1Y', 'N/A'),
        '종목코드': data.get('종목코드', 'N/A'),
        '네이버url': data.get('네이버url', 'N/A'),
    }

    print(ordered_data)

    return ordered_data

def main():
    parser = argparse.ArgumentParser(description="업종명에 따른 종목 정보를 크롤링합니다.")
    parser.add_argument('upjong_name', type=str, nargs='?', help='업종명을 입력하세요.')
    parser.add_argument('option', type=str, nargs='?', help='옵션: 퀀트 정보를 가져오려면 "퀀트"를 입력하세요.')
    args = parser.parse_args()
    
    upjong_list = fetch_upjong_list_API()
    
    if args.upjong_name:
        # 업종명을 입력받은 경우
        upjong_map = {업종명: (등락률, 링크) for 업종명, 등락률, 링크 in upjong_list}
        if args.upjong_name in upjong_map:
            등락률, 링크 = upjong_map[args.upjong_name]
            if args.option == '퀀트':
                # 퀀트 정보를 가져오는 경우
                print(f"\n업종명: {args.upjong_name} - 퀀트 정보")

                # 종목 정보를 가져옵니다.
                stock_info = fetch_stock_info_in_upjong(링크)
                if stock_info:
                    all_quant_data = []
                    for 종목명, _, _, _, 종목링크 in stock_info:
                        # 종목 링크에서 종목 코드를 추출
                        stock_code = 종목링크.split('=')[-1]  # 'code=종목코드' 형식으로 링크가 제공된다고 가정
                        quant_data = fetch_stock_info_quant(stock_code)
                        if quant_data:
                            all_quant_data.append(quant_data)
                    
                    # 엑셀 파일로 저장
                    excel_file_name = f'{args.upjong_name}_quant.xlsx'
                    df = pd.DataFrame(all_quant_data)
                    df.to_excel(excel_file_name, index=False, engine='openpyxl')
                    
                    print(f'퀀트 정보가 {excel_file_name} 파일에 저장되었습니다.')
                else:
                    print("종목 정보를 가져오는 데 문제가 발생했습니다.")
            else:
                # 종목 정보를 가져오는 경우
                stock_info = fetch_stock_info_in_upjong(링크)
                if stock_info:
                    print(f'\n업종명: {args.upjong_name}')
                    print(f"{'종목명':<20} {'현재가':<10} {'전일비':<10} {'등락률':<10}")
                    for 종목명, 현재가, 전일비, 등락률, _ in stock_info:  # 링크는 무시
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


# 함수 사용 예
if __name__ == "__main__":
    # main()
    upjong_list = fetch_upjong_list_API()
    for item in upjong_list:
        print(item)

