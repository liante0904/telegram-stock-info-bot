import argparse
import csv
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd  # pandas를 추가합니다
import requests
from datetime import datetime, timedelta
import json

def fetch_stock_yield_by_period(stock_code=None, date=None):
    # stock_code가 제공되지 않았을 때 에러 처리
    if not stock_code:
        print("Error: stock_code is required but was not provided.")
        return {"error": "stock_code is required"}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def fetch_data(url):
        # print(f"Fetching data from: {url}")  # Debugging message
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data: Status code {response.status_code}")
            return None

    # 현재 가격 가져오기
    basic_info_url = f'https://m.stock.naver.com/api/stock/{stock_code}/basic'
    basic_data = fetch_data(basic_info_url)

    if not basic_data:
        return {}

    current_price = int(basic_data['closePrice'].replace(',', ''))

    # 날짜별 가격 가져오기
    def fetch_past_price(days_ago):
        past_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y%m%d')
        trend_url = f'https://m.stock.naver.com/api/stock/{stock_code}/trend?pageSize=1&bizdate={past_date}'
        trend_data = fetch_data(trend_url)
        
        if trend_data:
            return int(trend_data[0]['closePrice'].replace(',', ''))
        return None

    # 수익률 계산
    def calculate_return(past_price):
        if past_price is not None:
            percentage_change = round((current_price / past_price - 1) * 100, 2)
            return "{:.2f}".format(percentage_change)
        return None

    # 1D, 1M, 6M, YTD, 1Y 수익률 계산
    timeframes = {
        '1D': 1,
        '1W': 7,
        '1M': 30,
        '3M': 90,        
        '6M': 180,
        'YTD': (datetime.now() - datetime(datetime.now().year, 1, 1)).days,
        '1Y': 365
    }

    returns = {key: calculate_return(fetch_past_price(days)) for key, days in timeframes.items()}

    return returns


def main():
    fetch_stock_yield_by_period('005930')

if __name__ == '__main__':
    main()
