import os
import sys
import requests
import pandas as pd
import math
import subprocess
import concurrent.futures
from tqdm import tqdm
from datetime import datetime
from modules.naver_upjong_quant import fetch_stock_info_quant_API

# API 기본 URL
kospi_url = "https://m.stock.naver.com/api/stocks/marketValue/KOSPI"
kosdaq_url = "https://m.stock.naver.com/api/stocks/marketValue/KOSDAQ"
# 최대 스레드 수
max_workers = 4

# 요청 헤더
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def ensure_directory(path):
    """폴더가 존재하지 않으면 생성"""
    if not os.path.exists(path):
        os.makedirs(path)

def fetch_all_stocks(base_url, market_name):
    params = {"page": 1, "pageSize": 100}
    response = requests.get(base_url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"{market_name} 첫 페이지 요청 실패: {response.status_code}")
        return []
    
    data = response.json()
    total_count = data.get("totalCount", 0)
    if total_count == 0:
        print(f"{market_name}에서 totalCount를 가져올 수 없습니다.")
        return []
    
    page_size = 100
    total_pages = math.ceil(total_count / page_size)
    print(f"{market_name} - 총 종목 수: {total_count}, 총 페이지 수: {total_pages}")
    
    all_stocks = []
    etf_etn_stocks = []
    for page in tqdm(range(1, total_pages + 1), desc=f"Fetching {market_name}"):
        params = {"page": page, "pageSize": page_size}
        response = requests.get(base_url, headers=headers, params=params)
        
        if response.status_code == 200:
            page_data = response.json()
            stocks = page_data.get("stocks", [])
            for stock in stocks:
                stock_info = {
                    "종목코드": stock.get("itemCode", ""),
                    "종목명": stock.get("stockName", ""),
                    "시가총액(억)": int(stock.get("marketValue", 0).replace(",", "")),
                }
                if stock.get("stockEndType") in ["etf", "etn"]:
                    etf_etn_stocks.append(stock_info)
                else:
                    all_stocks.append(stock_info)
        else:
            print(f"{market_name} 페이지 {page} 요청 실패: {response.status_code}")
    
    return all_stocks, etf_etn_stocks

def fetch_quant_data(stock_info):
    stock_code = stock_info["종목코드"]
    url = f"https://m.stock.naver.com/item/main.nhn#/stocks/{stock_code}/total"
    quant_data = fetch_stock_info_quant_API(stock_code, url)
    return quant_data if quant_data else {}

def add_quant_data(df, market_name):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        quant_data_list = list(tqdm(executor.map(fetch_quant_data, df.to_dict('records')), total=len(df), desc=f"Fetching Quant Data for {market_name}"))
    
    quant_df = pd.DataFrame(quant_data_list)
    df = pd.concat([df, quant_df], axis=1)
    df = df.sort_values(by="시가총액(억)", ascending=False)
    df = df.loc[:, ~df.columns.duplicated()]
    return df

def send_to_telegram():
    script_path = "/home/ubuntu/sh/sendDocument.sh"
    result = subprocess.run(["/bin/bash", script_path], capture_output=True, text=True)
    print("텔레그램 전송 스크립트 실행 결과:")
    print(result.stdout)
    print(result.stderr)

def main():
    # 전송 여부 체크 전 텔레그램 전송(최초 실행시 이미 발송되지 않을 수 있음)
    send_to_telegram()
    
    today_date = datetime.today().strftime('%y%m%d')
    send_folder = "send"
    ensure_directory(send_folder)
    
    file_name = f"KR_stock_screening_{today_date}.xlsx"
    file_path = os.path.join(send_folder, file_name)
    
    if os.path.exists(file_path):
        print(f"{file_name} 파일이 이미 존재합니다. 프로그램을 종료합니다.")
        return
    
    kospi_stocks, kospi_etf_etn = fetch_all_stocks(kospi_url, "KOSPI")
    kosdaq_stocks, kosdaq_etf_etn = fetch_all_stocks(kosdaq_url, "KOSDAQ")
    
    df_kospi = pd.DataFrame(kospi_stocks)
    df_kosdaq = pd.DataFrame(kosdaq_stocks)
    df_etf_etn = pd.DataFrame(kospi_etf_etn + kosdaq_etf_etn)
    
    df_kospi = add_quant_data(df_kospi, "KOSPI")
    df_kosdaq = add_quant_data(df_kosdaq, "KOSDAQ")
    df_etf_etn = add_quant_data(df_etf_etn, "ETF_ETN")
    
    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
        df_kospi.to_excel(writer, sheet_name="KOSPI", index=False)
        df_kosdaq.to_excel(writer, sheet_name="KOSDAQ", index=False)
        df_etf_etn.to_excel(writer, sheet_name="ETF_ETN", index=False)
    
    print(f"\n데이터가 '{file_name}' 파일에 저장되었습니다. (시트: KOSPI, KOSDAQ, ETF_ETN)")
    
    send_to_telegram()
    
    print(f"{file_name} 파일을 send 폴더로 이동 완료.")

if __name__ == '__main__':
    main()
