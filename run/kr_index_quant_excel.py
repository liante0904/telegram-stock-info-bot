import os
import sys
import pandas as pd
import requests
from openpyxl import Workbook
from dotenv import load_dotenv
from datetime import datetime

# .env 파일 로드
load_dotenv()

# .env 파일에서 URL 템플릿 읽기
NAVER_API_KR_INDEX = os.getenv("NAVER_API_KR_INDEX")

# Import the quant API module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.naver_upjong_quant import fetch_stock_info_quant_API

def fetch_stock_data(market_type, page=1, page_size=60):
    """
    Fetch stock data for the given market type and page number.
    
    :param market_type: "KOSPI" or "KOSDAQ"
    :param page: Page number for pagination
    :param page_size: Number of items per page
    :return: List of stock data
    """
    url = NAVER_API_KR_INDEX.format(market_type=market_type)
    params = {
        "pageSize": page_size,
        "page": page,
        "type": "object"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        stocks = data.get("stocks", [])
        return stocks
    else:
        print(f"Failed to fetch data for {market_type}. HTTP Status: {response.status_code}")
        return []

def fetch_all_stocks(market_type):
    """
    Fetch all stocks for the given market type by iterating through all pages.
    
    :param market_type: "KOSPI" or "KOSDAQ"
    :return: List of all stock data
    """
    all_stocks = []
    page = 1

    while True:
        stocks = fetch_stock_data(market_type, page)
        print(f"Fetched {len(stocks)} stocks from {market_type} (Page {page})")

        # Filter out SPAC stocks
        filtered_stocks = [
            stock for stock in stocks
            if not (stock["itemCode"].startswith("4") and "스팩" in stock["stockName"])
        ]

        if not filtered_stocks:  # If the filtered stocks list is empty, break the loop
            break
        all_stocks.extend(filtered_stocks)
        page += 1

    return all_stocks

def fetch_quant_data_for_all_stocks(stocks):
    """
    Fetch quant data for all stocks in the given list.

    :param stocks: List of stock data with "itemCode" and "stockName"
    :return: List of dictionaries containing quant data
    """
    all_quant_data = []

    for stock in stocks:
        stock_code = stock["itemCode"]
        stock_name = stock["stockName"]
        url = f"https://m.stock.naver.com/domestic/stock/{stock_code}"

        quant_data = fetch_stock_info_quant_API(stock_code, url)
        if quant_data:
            quant_data["종목코드"] = stock_code
            quant_data["종목명"] = stock_name
            all_quant_data.append(quant_data)

    return all_quant_data

def save_quant_data_to_excel(kospi_quant_data, kosdaq_quant_data):
    """
    Save quant data to an Excel file with 'KOSPI' and 'KOSDAQ' sheets.

    :param kospi_quant_data: List of KOSPI quant data
    :param kosdaq_quant_data: List of KOSDAQ quant data
    """
    today_date = datetime.today().strftime('%y%m%d')
    file_name = f"quant_data_{today_date}.xlsx"

    with pd.ExcelWriter(file_name, engine="openpyxl") as writer:
        if kospi_quant_data:
            df_kospi = pd.DataFrame(kospi_quant_data)
            df_kospi.to_excel(writer, sheet_name="KOSPI", index=False)

        if kosdaq_quant_data:
            df_kosdaq = pd.DataFrame(kosdaq_quant_data)
            df_kosdaq.to_excel(writer, sheet_name="KOSDAQ", index=False)

    print(f"퀀트 데이터가 {file_name} 파일에 저장되었습니다.")

def main():
    print("Fetching KOSPI stocks...")
    kospi_stocks = fetch_all_stocks("KOSPI")

    print("Fetching KOSDAQ stocks...")
    kosdaq_stocks = fetch_all_stocks("KOSDAQ")

    print("Fetching KOSPI quant data...")
    kospi_quant_data = fetch_quant_data_for_all_stocks(kospi_stocks)

    print("Fetching KOSDAQ quant data...")
    kosdaq_quant_data = fetch_quant_data_for_all_stocks(kosdaq_stocks)

    print("Saving quant data to Excel...")
    save_quant_data_to_excel(kospi_quant_data, kosdaq_quant_data)

if __name__ == "__main__":
    main()
