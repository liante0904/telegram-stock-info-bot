from pykrx import stock

def get_tickers_and_names(market):
    tickers = stock.get_market_ticker_list(market=market)
    tickers_names = {}
    
    for ticker in tickers:
        name = stock.get_market_ticker_name(ticker)
        tickers_names[ticker] = name
        # time.sleep(0.1)  # 너무 빠른 요청으로 인한 문제를 방지하기 위해 딜레이 추가
    
    return tickers_names

def get_all_tickers_and_names():
    kospi_tickers = get_tickers_and_names(market="KOSPI")
    kosdaq_tickers = get_tickers_and_names(market="KOSDAQ")
    
    return {
        "KOSPI": kospi_tickers,
        "KOSDAQ": kosdaq_tickers
    }

def main():
    r = get_all_tickers_and_names()
    print(r)
if __name__ == '__main__':
    main()