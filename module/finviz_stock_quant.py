from finvizfinance.quote import finvizfinance

def fetch_worldstock_info(stock_code):
    """finviz 용으로 재 작성"""
    stock = finvizfinance(stock_code)
    
    # Fundament
    stock_fundament = stock.ticker_fundament()
    print(stock_fundament)
    # Description
    # stock_description = stock.ticker_description()
    # print(stock_description)


    
    # stock_data = stock_fundament.json()
    print(stock_fundament.get('Company'))
    if stock.isETF:
        data = {
            '종목명': stock_fundament['Company'],  # 'Company': 'Utilities Select Sector SPDR ETF'
            'PER': 'N/A',  # 'P/E': N/A (ETF에는 PER 정보가 없음)
            'fwdPER': 'N/A',  # 'Forward P/E': N/A (ETF에는 예상 PER 정보가 없음)
            'PBR': 'N/A',  # 'P/B': N/A (ETF에는 PBR 정보가 없음)
            '배당수익률': stock_fundament['Dividend TTM'],  # 'Dividend TTM': '2.19 (2.73%)'
            '예상배당수익률': 'N/A',  # 'Dividend Est.': N/A (ETF에는 예상 배당수익률 정보가 없음)
            'ROE': 'N/A',  # 'ROE': N/A (ETF에는 ROE 정보가 없음)
            '현재가': stock_fundament['Price'],  # 'Price': '80.33'
            '전일비': stock_fundament['Prev Close'],  # 'Prev Close': '80.08'
            '등락률': stock_fundament['Change'],  # 'Change': '0.31%'
            '비고(메모)': 'N/A',  # 'Trades': N/A (ETF에는 비고 정보가 없음)
            '1D': stock_fundament['Change'],  # 'Change': '0.31%'
            '1W': stock_fundament['Perf Week'],  # 'Perf Week': '1.50%'
            '1M': stock_fundament['Perf Month'],  # 'Perf Month': '6.81%'
            '3M': stock_fundament['Perf Quarter'],  # 'Perf Quarter': '15.18%'
            '6M': stock_fundament['Perf Half Y'],  # 'Perf Half Y': '25.79%'
            'YTD': stock_fundament['Perf YTD'],  # 'Perf YTD': '26.84%'
            '1Y': stock_fundament['Perf Year'],  # 'Perf Year': '26.68%'
            '종목코드': stock.ticker,  # 'Ticker': N/A (ETF에는 종목 코드 정보가 없음)
            '네이버url': '',  # 'Naver URL': N/A
            'FinvizUrl': stock.quote_url  # 'Finviz URL'
        }
    else:
        data = {
            '종목명': stock_fundament['Company'],  # 'Company': 'Tesla Inc'
            'PER': stock_fundament['P/E'],  # 'P/E': '66.91'
            'fwdPER': stock_fundament['Forward P/E'],  # 'Forward P/E': '74.86'
            'PBR': stock_fundament['P/B'],  # 'P/B': '11.45'
            '배당수익률': stock_fundament['Dividend TTM'],  # 'Dividend TTM': '-'
            '예상배당수익률': stock_fundament['Dividend Est.'],  # 'Dividend Est.': '-'
            'ROE': stock_fundament['ROE'],  # 'ROE': '21.13%'
            '현재가': stock_fundament['Price'],  # 'Price': '238.25'
            '전일비': stock_fundament['Prev Close'],  # 'Prev Close': '243.92'
            '등락률': stock_fundament['Change'],  # 'Change': '-2.32%'
            '비고(메모)': stock_fundament['Trades'],  # 'Trades': '\n\n'
            '1D': stock_fundament['Change'],  # 'Change': '-2.32%'
            '1W': stock_fundament['Perf Week'],  # 'Perf Week': '3.46%'
            '1M': stock_fundament['Perf Month'],  # 'Perf Month': '6.71%'
            '3M': stock_fundament['Perf Quarter'],  # 'Perf Quarter': '30.18%'
            '6M': stock_fundament['Perf Half Y'],  # 'Perf Half Y': '37.86%'
            'YTD': stock_fundament['Perf YTD'],  # 'Perf YTD': '-4.12%'
            '1Y': stock_fundament['Perf Year'],  # 'Perf Year': '-9.27%'
            '종목코드': stock.ticker,  # 'Ticker': 'TSLA'
            '네이버url': '',  # 'Naver URL': 'NDX, S&P 500'
            'FinvizUrl': stock.quote_url  # 'Finviz URL'
        }


    print(data)

    return data
