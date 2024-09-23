from finvizfinance.quote import finvizfinance

stock = finvizfinance('tsla')
# chart
print(stock.ticker_charts())
# Fundament
stock_fundament = stock.ticker_fundament()
print(stock_fundament)
# Description
stock_description = stock.ticker_description()
print(stock_description)

'''
{
    '종목명': json.Company,  # 'Company': 'Tesla Inc'
    'PER': json.PE,  # 'P/E': '66.91'
    'fwdPER': json.Forward_PE,  # 'Forward P/E': '74.86'
    'PBR': json.PB,  # 'P/B': '11.45'
    '배당수익률': json.Dividend_TTM,  # 'Dividend TTM': '-'
    '예상배당수익률': json.Dividend_Est,  # 'Dividend Est.': '-'
    'ROE': json.ROE,  # 'ROE': '21.13%'
    '현재가': json.Price,  # 'Price': '238.25'
    '전일비': json.Prev_Close,  # 'Prev Close': '243.92'
    '등락률': json.Change,  # 'Change': '-2.32%'
    '비고(메모)': json.Trades,  # 'Trades': '\n\n'
    '1D': json.Change,  # 'Change': '-2.32%'
    '1W': json.Perf_Week,  # 'Perf Week': '3.46%'
    '1M': json.Perf_Month,  # 'Perf Month': '6.71%'
    '3M': json.Perf_Quarter,  # 'Perf Quarter': '30.18%'
    '6M': json.Perf_Half_Y,  # 'Perf Half Y': '37.86%'
    'YTD': json.Perf_YTD,  # 'Perf YTD': '-4.12%'
    '1Y': json.Perf_Year,  # 'Perf Year': '-9.27%'
    '종목코드': json.Ticker,  # 'Ticker': 'TSLA'
    '네이버url': json.Naver_URL  # 'Naver URL': 'NDX, S&P 500'
}
'''