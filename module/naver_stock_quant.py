import requests
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.CacheManager import CacheManager
from module.naver_upjong_quant import fetch_stock_info_quant_API

import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd

def fetch_dividend_stock_list_API(requested_stock_count=0):
    # 기본 세팅
    page=1 
    # API당 fetch 수(최대)
    pageSize = 100

    # CacheManager 인스턴스 생성
    cache_manager = CacheManager("cache", "dividend_stock")

    # 전체 데이터를 담을 리스트
    all_data = []

    # 첫 페이지 호출하여 전체 페이지 수와 종목 수를 알아냄
    first_page_url = f"https://m.stock.naver.com/api/stocks/dividend/rate?page=1&pageSize={pageSize}"
    response = requests.get(first_page_url)

    if response.status_code != 200:
        raise Exception(f"API 요청 실패: {response.status_code}")

    first_page_data = response.json()
    # nationCode 값을 0번째 인덱스에서 가져오기
    nation_code = first_page_data['dividends'][0]['stockExchangeType']['nationCode']
    totalCount  = first_page_data.get('totalCount', 0)  # totalCount 추출, 없을 경우 기본값 0
    print(f"0번째 인덱스 종목의 Nation Code: {nation_code}")
    print(f"전체 종목수 : {totalCount}")
    total_count = first_page_data.get('totalCount', 0)
    total_pages = (total_count // pageSize) + (1 if total_count % pageSize > 0 else 0)

    # requested_stock_count가 0이거나 값이 없는 경우 전체 데이터를 가져옴
    if requested_stock_count <= 0:
        requested_stock_count = total_count

    # 데이터를 수집할 페이지 수 계산 (requested_stock_count에 맞게)
    required_pages = (requested_stock_count // pageSize) + (1 if requested_stock_count % pageSize > 0 else 0)
    
    # 전체 페이지 수와 비교하여 최소 페이지 수로 설정
    if page <= 0:
        page = required_pages
    else:
        page = min(page, required_pages)

    # 지정된 페이지 수만큼 데이터를 수집
    for p in range(1, page + 1):
        # 캐시 키를 페이지별로 구분하여 설정
        cache_key = f'dividend_stock_{p}'

        # 캐시가 유효한지 확인
        if cache_manager.is_cache_valid(cache_key, nation_code):
            print(f"[DEBUG] 유효한 캐시를 발견했습니다. (Page {p})")
            data = cache_manager.load_cache(cache_key)
        else:
            print(f"[DEBUG] 유효한 캐시가 없으므로 API를 호출합니다. (Page {p})")
            # API 호출 URL
            url = f"https://m.stock.naver.com/api/stocks/dividend/rate?page={p}&pageSize={pageSize}"
            response = requests.get(url)

            if response.status_code != 200:
                raise Exception(f"API 요청 실패: {response.status_code}")

            data = response.json()

            # 데이터를 캐시에 저장
            cache_manager.save_cache(cache_key, data)

        # 수집된 데이터를 리스트에 추가
        all_data.extend(data.get('dividends', []))  # 'dividends' 키로 데이터 추출

        # 수집된 데이터가 requested_stock_count에 도달하면 종료
        if len(all_data) >= requested_stock_count:
            print(f"[DEBUG] 요청한 {requested_stock_count}개의 데이터를 모두 수집했습니다.")
            break

    # 수집된 데이터가 requested_stock_count보다 많으면 잘라내기
    return all_data[:requested_stock_count], totalCount


def save_stock_data_to_excel(data, file_name='dividend_stock_data.xlsx'):
    # 데이터 프레임으로 변환
    df = pd.DataFrame(data, columns=['stockName', 'itemCode', 'dividendRate'])
    
    # 엑셀 파일 생성
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Dividend Stock Data'
    
    # 헤더 추가
    headers = ['종목명', '종목코드', '배당수익률', '시장구분', 'PER', 'fwdPER', 'PBR', '예상배당수익률', 'ROE', '현재가', '전일비', '등락률', '비고(메모)', '1D', '1W', '1M', '3M', '6M', 'YTD', '1Y', '네이버url']
    ws.append(headers)
    
    # 데이터 추가
    for row in dataframe_to_rows(df, index=False, header=False):
        # ws.append(row)
        # itemCode 값을 출력
        item_code_index = df.columns.get_loc('itemCode')
        stock_code = row[item_code_index]
        
        # fetch_stock_info_quant_API 호출 및 데이터 추가
        stock_info = fetch_stock_info_quant_API(stock_code=stock_code)
        
        # 데이터 추가
        info_row = [
            stock_info['종목명'],
            stock_info['종목코드'],
            stock_info['배당수익률'],
            stock_info['시장구분'],
            stock_info['PER'],
            stock_info['fwdPER'],
            stock_info['PBR'],
            stock_info['예상배당수익률'],
            stock_info['ROE'],
            stock_info['현재가'],
            stock_info['전일비'],
            stock_info['등락률'],
            stock_info['비고(메모)'],
            stock_info['1D'],
            stock_info['1W'],
            stock_info['1M'],
            stock_info['3M'],
            stock_info['6M'],
            stock_info['YTD'],
            stock_info['1Y'],
            stock_info['네이버url']
        ]
        ws.append(info_row)
    
    # 파일 저장
    wb.save(file_name)
    print(f"[INFO] 엑셀 파일 '{file_name}'이 저장되었습니다.")

def main():
    all_data = []
    # fetch_stock_yield_by_period('005930')
    # 수집된 데이터를 리스트에 추가
    all_data, dividend_total_stock_count = fetch_dividend_stock_list_API(requested_stock_count=101)
    # 엑셀 파일로 저장
    save_stock_data_to_excel(all_data)

if __name__ == '__main__':
    main()

