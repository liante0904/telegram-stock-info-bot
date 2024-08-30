from pykrx import stock

def is_etf(ticker):
    # 모든 ETF 종목들의 티커 리스트를 가져옵니다.
    etf_tickers = stock.get_etf_ticker_list('20240813')
    
    
    # 주어진 티커가 ETF 리스트에 있는지 확인합니다.
    return ticker in etf_tickers

# 예시: 6자리 종목 코드로 ETF 여부를 확인
ticker = "069500"  # 예시로 KODEX 200 ETF의 종목 코드
if is_etf(ticker):
    print(f"{ticker}는 ETF입니다.")
else:
    print(f"{ticker}는 ETF가 아닙니다.")
