import time
import json
from pykrx import stock

def get_tickers_and_names(market):
    tickers = stock.get_market_ticker_list(market=market)
    tickers_names = {}
    
    for ticker in tickers:
        
        name = stock.get_market_ticker_name(ticker)
        tickers_names[ticker] = name
    
    return tickers_names

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    kospi_tickers = get_tickers_and_names(market="KOSPI")
    time.sleep(1)  # 1초 딜레이
    kosdaq_tickers = get_tickers_and_names(market="KOSDAQ")
    time.sleep(1)  # 1초 딜레이
    print("KOSPI Tickers and Names:")
    for ticker, name in kospi_tickers.items():
        print(f"{ticker}: {name}")
    
    print("\nKOSDAQ Tickers and Names:")
    for ticker, name in kosdaq_tickers.items():
        print(f"{ticker}: {name}")
    
    # JSON 파일로 저장
    save_to_json({
        "KOSPI": kospi_tickers,
        "KOSDAQ": kosdaq_tickers
    }, "tickers_and_names.json")

if __name__ == "__main__":
    main()
