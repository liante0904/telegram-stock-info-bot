from pykrx import stock
from pykrx import bond

def get_period_returns(ticker, start_date, end_date):
    # 주식 데이터를 가져옵니다
    df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
    
    # 기간 수익률을 계산합니다
    start_price = df['종가'].iloc[0]
    end_price = df['종가'].iloc[-1]
    period_return = (end_price - start_price) / start_price * 100
    
    return period_return

tickers = stock.get_index_ticker_list()
for ticker in tickers:
    ticker_name = stock.get_index_ticker_name(ticker)
    print(stock.get_index_ticker_name(ticker), ticker)
    pdf = stock.get_index_portfolio_deposit_file(str(ticker))
    print('섹터 구성종목코드:', pdf)
    for p_ticker in pdf:
        ticker = p_ticker  # 삼성전자 티커
        start_date = '2023-01-01'
        end_date = '2023-12-31'

        return_rate = get_period_returns(ticker, start_date, end_date)
        print(f"{start_date}부터 {end_date}까지의 {stock.get_market_ticker_name(p_ticker)}{ticker}의 수익률: {return_rate:.2f}%")
    break