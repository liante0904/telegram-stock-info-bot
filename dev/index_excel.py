import requests
from openpyxl import Workbook
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# .env 파일에서 URL 템플릿 읽기
NAVER_API_KR_INDEX = os.getenv("NAVER_API_KR_INDEX")
print(NAVER_API_KR_INDEX)

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
        if not stocks:  # If the stocks list is empty, break the loop
            break
        all_stocks.extend(stocks)
        page += 1

    return all_stocks

def save_to_excel(kospi_stocks, kosdaq_stocks, file_name="stocks.xlsx"):
    """
    Save stock data to an Excel file with 'KOSPI' and 'KOSDAQ' sheets.
    
    :param kospi_stocks: List of KOSPI stocks
    :param kosdaq_stocks: List of KOSDAQ stocks
    :param file_name: Name of the Excel file to save
    """
    wb = Workbook()
    
    # KOSPI Sheet
    ws_kospi = wb.active
    ws_kospi.title = "코스피"
    ws_kospi.append(["종목 코드", "종목명"])  # Header
    for stock in kospi_stocks:
        ws_kospi.append([stock["itemCode"], stock["stockName"]])
    
    # KOSDAQ Sheet
    ws_kosdaq = wb.create_sheet(title="코스닥")
    ws_kosdaq.append(["종목 코드", "종목명"])  # Header
    for stock in kosdaq_stocks:
        ws_kosdaq.append([stock["itemCode"], stock["stockName"]])
    
    # Save Excel File
    wb.save(file_name)
    print(f"Data saved to {file_name}")

# Fetch KOSPI and KOSDAQ stocks
kospi_stocks = fetch_all_stocks("KOSPI")
kosdaq_stocks = fetch_all_stocks("KOSDAQ")

# Save to Excel
save_to_excel(kospi_stocks, kosdaq_stocks)
