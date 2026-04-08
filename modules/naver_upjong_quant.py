from datetime import datetime
import argparse
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd  # pandas를 추가합니다
import sys
import os

# 현재 스크립트의 상위 디렉터리를 모듈 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.CacheManager import CacheManager
from utils.naver_stock_util import stock_fetch_yield_by_period, search_stock_code, get_industry_name, safe_float, safe_int, clean_numeric_dict
from modules.finviz_stock_quant import fetch_worldstock_info

# 전역 상수 설정
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
NUMERIC_KEYS = ['PER', 'fwdPER', 'PBR', '배당수익률', '예상배당수익률', 'ROE', '현재가', '전일비', '등락률', '1D', '1W', '1M', '3M', '6M', 'YTD', '1Y']

def fetch_upjong_list_API(nation_code):
    cache_manager = CacheManager("cache", "upjong")
    
    if cache_manager.is_cache_valid('upjong', nation_code):
        print("[DEBUG] 유효한 캐시를 발견했습니다.")
        return cache_manager.load_cache('upjong').get('result', [])
    
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
        cache_manager.save_cache('upjong', {'result': result, 'marketStatus': 'CLOSE'})
    
    return result

def fetch_stock_info_in_upjong(upjong_link):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
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

def fetch_stock_info_quant_API(stock_code=None, stock_name=None, url=None, reutersCode=None, date=None):
    if not any([stock_code, stock_name, url, reutersCode]):
        raise ValueError("Stock identification (code, name, url, or reutersCode) must be provided.")
    
    # 1. 종목 정보 기본 조회
    results = search_stock_code(stock_code or stock_name or reutersCode)
    if not results:
        return {}
    
    target = results[0]
    stock_code, stock_name, url = target['code'], target['name'], target['url']
    reutersCode, nationCode = target['reutersCode'], target['nationCode']
    
    # 2. 캐시 확인
    cache_manager = CacheManager("cache", "stock")
    if cache_manager.is_cache_valid(stock_code, nationCode):
        return cache_manager.load_cache(stock_code).get('result', {})
    
    # 3. 데이터 수집 (국내/해외 분기)
    try:
        if 'domestic' in url:
            data = fetch_domestic_stock_info(stock_code, reutersCode, date)
        elif 'worldstock' in url:
            # Finviz 또는 Naver World API 사용 (기존 로직 유지)
            ticker = url.split('/')[-2]
            if '.T' in ticker: # 일본 주식 등은 Naver World API 선호 가능 (필요시 확장)
                data = fetch_worldstock_info_NAVER(DEFAULT_HEADERS, stock_code, reutersCode)
            else:
                data = fetch_worldstock_info(stock_code)
        else:
            raise ValueError("Invalid stock URL format.")
    except Exception as e:
        print(f"[ERROR] Failed to fetch quant data for {stock_name}: {e}")
        return {}

    # 4. 데이터 정제 및 공통 키 설정
    data['종목코드'] = str(stock_code)
    data['네이버url'] = url
    
    # 숫자형 변환 및 순서 정리
    ordered_data = {
        '종목명': data.get('종목명', stock_name),
        '시장구분': data.get('시장구분', 'N/A'),
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
        '업종': data.get('업종', 'N/A'),
        '1D': data.get('등락률', 'N/A'),
        '1W': data.get('1W', 'N/A'),
        '1M': data.get('1M', 'N/A'),
        '3M': data.get('3M', 'N/A'),
        '6M': data.get('6M', 'N/A'),
        'YTD': data.get('YTD', 'N/A'),
        '1Y': data.get('1Y', 'N/A'),
        '종목코드': data.get('종목코드', 'N/A'),
        '네이버url': data.get('네이버url', 'N/A'),
    }

    if 'worldstock' in url:
        ordered_data['FinvizUrl'] = data.get('FinvizUrl', 'N/A')

    # 숫자 변환 유틸 적용
    ordered_data = clean_numeric_dict(ordered_data, NUMERIC_KEYS)
    
    # 5. 캐시 저장 및 반환
    cache_manager.save_cache(stock_code, {'result': ordered_data})
    return ordered_data

def fetch_domestic_stock_info(stock_code, reutersCode, date=None):
    """국내 주식 상세 정보 조회 (API 기반)"""
    basic_url = f'https://m.stock.naver.com/api/stock/{stock_code}/basic'
    integ_url = f'https://m.stock.naver.com/api/stock/{stock_code}/integration'
    finance_url = f'https://m.stock.naver.com/api/stock/{stock_code}/finance/annual'
    
    data = {}
    
    # Basic 정보
    res_basic = requests.get(basic_url, headers=DEFAULT_HEADERS).json()
    data.update({
        '종목명': res_basic.get('stockName'),
        '시장구분': res_basic.get('stockExchangeType', {}).get('nameEng'),
        '현재가': res_basic.get('closePrice'),
        '전일비': res_basic.get('compareToPreviousClosePrice'),
        '등락률': res_basic.get('fluctuationsRatio')
    })
    
    # Integration 정보 (PER, PBR, 업종 등)
    res_integ = requests.get(integ_url, headers=DEFAULT_HEADERS).json()
    total_infos = {info['key']: info['value'] for info in res_integ.get('totalInfos', [])}
    data.update({
        'PER': total_infos.get('PER', 'N/A').replace('배', ''),
        'fwdPER': total_infos.get('추정PER', 'N/A').replace('배', ''),
        'PBR': total_infos.get('PBR', 'N/A').replace('배', ''),
        '배당수익률': total_infos.get('배당수익률', 'N/A').replace('%', ''),
        '업종': get_industry_name(res_integ.get('industryCode', ''))
    })
    
    # 재무 정보 (ROE, 예상 배당)
    res_fin = requests.get(finance_url, headers=DEFAULT_HEADERS).json()
    if res_fin.get('financeInfo'):
        current_year = str(datetime.now().year)
        row_list = res_fin['financeInfo'].get('rowList', [])
        
        # 특정 타이틀의 값을 찾는 헬퍼 함수
        def get_fin_val(title):
            row = next((item for item in row_list if item['title'] == title), None)
            if row and row['columns']:
                # 최신 연도 데이터 탐색
                available_years = [k for k in row['columns'].keys() if k.startswith(current_year)]
                target_year = max(available_years) if available_years else max(row['columns'].keys(), default=None)
                if target_year:
                    return row['columns'][target_year].get('value')
            return 'N/A'

        data['ROE'] = get_fin_val('ROE')
        est_div = safe_int(get_fin_val('주당배당금'))
        curr_price = safe_int(data['현재가'])
        if est_div != 'N/A' and curr_price != 'N/A' and curr_price > 0:
            data['예상배당수익률'] = round(est_div / curr_price * 100, 2)
        else:
            data['예상배당수익률'] = 'N/A'

    # 기간 수익률 추가
    yield_data = stock_fetch_yield_by_period(stock_code, date)
    data.update(yield_data)
    
    return data

def fetch_worldstock_info_NAVER(headers, stock_code, reutersCode):
    api_url = f'https://api.stock.naver.com/stock/{reutersCode}/basic'
    print('='*5 , 'fetch_worldstock_info', '='*5 )
    print(api_url)
    try:
        api_response = requests.get(api_url, headers=headers)
        if api_response.status_code != 200:
            raise Exception(f"Failed to fetch API data: Status code {api_response.status_code}")
    except Exception as e:
        print(f"Error fetching API data: {e}")
        return {}
    
    stock_data = api_response.json()

    data = {
        '종목명': stock_data.get('stockName', 'N/A'),
        '시장구분': stock_data.get('stockExchangeName', 'N/A'),
        '현재가': stock_data.get('closePrice', 'N/A'),  # 현재가는 closePrice
        '전일비': stock_data.get('compareToPreviousClosePrice', 'N/A'),  # 전일비는 compareToPreviousClosePrice
        '등락률': stock_data.get('fluctuationsRatio', 'N/A'),  # 등락률은 fluctuationsRatio
        '종목코드': stock_data.get('itemCode', 'N/A'),  # 주식종목코드
        '네이버url': stock_data.get('endUrl', 'N/A'),  # 네이버 url은 endUrl
        'reutersCode': stock_data.get('reutersCode', 'N/A')  # 네이버 고유 라우트코드
    }

    return data


def fetch_stock_info_quant(stock_code):
    """레거시 호환성을 위해 유지: 내부적으로 개선된 API 버전을 호출합니다."""
    return fetch_stock_info_quant_API(stock_code=stock_code)

def main():
    parser = argparse.ArgumentParser(description="업종명에 따른 종목 정보를 크롤링합니다.")
    parser.add_argument('upjong_name', type=str, nargs='?', help='업종명을 입력하세요.')
    parser.add_argument('option', type=str, nargs='?', help='옵션: 퀀트 정보를 가져오려면 "퀀트"를 입력하세요.')
    args = parser.parse_args()
    
    upjong_list = fetch_upjong_list_API('KOR')
    
    if args.upjong_name:
        # 업종명을 입력받은 경우
        upjong_map = {업종명: (등락률, 링크) for 업종명, 등락률, 링크 in upjong_list}
        if args.upjong_name in upjong_map:
            등락률, 링크 = upjong_map[args.upjong_name]
            if args.option == '퀀트':
                print(f"\n업종명: {args.upjong_name} - 퀀트 정보 수집 중...")
                stock_info = fetch_stock_info_in_upjong(링크)
                if stock_info:
                    all_quant_data = [fetch_stock_info_quant_API(stock_code=link.split('=')[-1]) for _, _, _, _, link in stock_info]
                    all_quant_data = [d for d in all_quant_data if d]
                    
                    excel_file_name = f'{args.upjong_name}_quant.xlsx'
                    pd.DataFrame(all_quant_data).to_excel(excel_file_name, index=False, engine='openpyxl')
                    print(f'퀀트 정보가 {excel_file_name} 파일에 저장되었습니다.')
            else:
                stock_info = fetch_stock_info_in_upjong(링크)
                if stock_info:
                    print(f'\n업종명: {args.upjong_name}')
                    for 종목명, 현재가, 전일비, 등락률, _ in stock_info:
                        print(f"{종목명:<20} {현재가:<10} {전일비:<10} {등락률:<10}")
        else:
            print("입력한 업종명이 올바르지 않습니다.")
    else:
        print("업종 목록:")
        for 업종명, 등락률, _ in upjong_list:
            print(f'업종명: {업종명}, 등락률: {등락률}')

if __name__ == "__main__":
    # main()
    pass