from finvizfinance.quote import finvizfinance

def fetch_worldstock_info(stock_code):
    """finviz 용으로 재 작성"""
    try:
        stock = finvizfinance(stock_code.replace('.','-'))  # 예: 'TSLA' 또는 'SPY'
        
        # Fundament
        stock_fundament = stock.ticker_fundament()

        if not stock_fundament:
            print(f"Error fetching fundamental data for {stock_code} from finviz.")
            return {
                '종목명': 'Error', 'PER': 'N/A', 'fwdPER': 'N/A', 'PBR': 'N/A', 
                '배당수익률': 'N/A', '예상배당수익률': 'N/A', 'ROE': 'N/A', '현재가': 'N/A', 
                '전일비': 'N/A', '등락률': 'N/A', '비고(메모)': 'Fundamental Data Not Found', '1D': 'N/A', 
                '1W': 'N/A', '1M': 'N/A', '3M': 'N/A', '6M': 'N/A', 'YTD': 'N/A', 
                '1Y': 'N/A', '종목코드': stock_code, '네이버url': '', 'FinvizUrl': ''
            }

        print(stock_fundament)
        # Description
        # stock_description = stock.ticker_description()
        # print(stock_description)

        # stock_data = stock_fundament.json()
        print(stock_fundament.get('Company'))
        if stock.isETF:
            data = {
                '종목명': stock_fundament.get('Company', 'N/A'),
                'PER': 'N/A',
                'fwdPER': 'N/A',
                'PBR': 'N/A',
                '배당수익률': stock_fundament.get('Dividend TTM', 'N/A'),
                '예상배당수익률': 'N/A',
                'ROE': 'N/A',
                '현재가': stock_fundament.get('Price', 'N/A'),
                '전일비': stock_fundament.get('Prev Close', 'N/A'),
                '등락률': stock_fundament.get('Change', 'N/A'),
                '비고(메모)': 'N/A',
                '1D': stock_fundament.get('Change', 'N/A'),
                '1W': stock_fundament.get('Perf Week', 'N/A'),
                '1M': stock_fundament.get('Perf Month', 'N/A'),
                '3M': stock_fundament.get('Perf Quarter', 'N/A'),
                '6M': stock_fundament.get('Perf Half Y', 'N/A'),
                'YTD': stock_fundament.get('Perf YTD', 'N/A'),
                '1Y': stock_fundament.get('Perf Year', 'N/A'),
                '종목코드': stock.ticker,
                '네이버url': '',
                'FinvizUrl': stock.quote_url
            }
        else:
            data = {
                '종목명': stock_fundament.get('Company', 'N/A'),
                'PER': stock_fundament.get('P/E', 'N/A'),
                'fwdPER': stock_fundament.get('Forward P/E', 'N/A'),
                'PBR': stock_fundament.get('P/B', 'N/A'),
                '배당수익률': stock_fundament.get('Dividend TTM', 'N/A'),
                '예상배당수익률': stock_fundament.get('Dividend Est.', 'N/A'),
                'ROE': stock_fundament.get('ROE', 'N/A'),
                '현재가': stock_fundament.get('Price', 'N/A'),
                '전일비': stock_fundament.get('Prev Close', 'N/A'),
                '등락률': stock_fundament.get('Change', 'N/A'),
                '비고(메모)': stock_fundament.get('Trades', 'N/A'),
                '1D': stock_fundament.get('Change', 'N/A'),
                '1W': stock_fundament.get('Perf Week', 'N/A'),
                '1M': stock_fundament.get('Perf Month', 'N/A'),
                '3M': stock_fundament.get('Perf Quarter', 'N/A'),
                '6M': stock_fundament.get('Perf Half Y', 'N/A'),
                'YTD': stock_fundament.get('Perf YTD', 'N/A'),
                '1Y': stock_fundament.get('Perf Year', 'N/A'),
                '종목코드': stock.ticker,
                '네이버url': '',
                'FinvizUrl': stock.quote_url
            }

        print(data)
        return data

    except Exception as e:
        print(f"Error fetching data for {stock_code} from finviz: {e}")
        # Return a dictionary with error values, maintaining the same structure
        return {
            '종목명': 'Error', 'PER': 'N/A', 'fwdPER': 'N/A', 'PBR': 'N/A', 
            '배당수익률': 'N/A', '예상배당수익률': 'N/A', 'ROE': 'N/A', '현재가': 'N/A', 
            '전일비': 'N/A', '등락률': 'N/A', '비고(메모)': f'Fetch Error: {e}', '1D': 'N/A', 
            '1W': 'N/A', '1M': 'N/A', '3M': 'N/A', '6M': 'N/A', 'YTD': 'N/A', 
            '1Y': 'N/A', '종목코드': stock_code, '네이버url': '', 'FinvizUrl': ''
        }
