import argparse
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import requests
from naver_stock_util import search_stock_code

# 국가별 종목 코드 접미사
TICKER_SUFFIXES = {
    'KOR': '.KS',  # 한국
    'USA': '',     # 미국
    'JPN': '.T'    # 일본
}



# 종목명과 국가 코드를 입력받아 해당 국가의 종목코드를 반환하는 함수
def get_ticker_symbol(stock_code, nation_code):
    # 미리 정의된 종목 코드와 접미사
    TICKER_SUFFIXES = {
        'KOR': '.KS',  # 한국 주식은 코스피 .KS 또는 코스닥 .KQ로 구분
        'USA': '',     # 미국 주식은 접미사 없음
        'JPN': '.T'    # 일본 주식은 .T 접미사 사용
    }
    if stock_code:
        # 종목 코드에 해당 국가 접미사 추가
        return stock_code + TICKER_SUFFIXES[nation_code]
    return None

def draw_dividend_yield_chart(ticker_symbol, nation_code):
    # 현재 날짜를 가져오기
    current_date = pd.Timestamp.now()

    # 주식 데이터 다운로드 (최소 5년 3개월 이전 데이터)
    ticker = yf.Ticker(ticker_symbol)
    new_stock_data = ticker.history(start=(current_date - pd.DateOffset(months=63)).strftime('%Y-%m-%d'))
    dividends = ticker.dividends

    # 타임존 정보가 있는 경우에만 tz_localize(None) 적용
    if new_stock_data.index.tz is not None:
        new_stock_data.index = new_stock_data.index.tz_localize(None)

    if dividends.index.tz is not None:
        dividends.index = dividends.index.tz_localize(None)

    # 배당 정보가 없는 일자를 제외하고 주가 데이터와 병합
    new_stock_data['Dividends'] = dividends.reindex(new_stock_data.index, fill_value=0)

    # 시가배당률 계산: (배당금 / 종가) * 100
    new_stock_data['Dividend Yield'] = 0  # 일단 0으로 초기화

    # 과거 배당금 추적 및 시가배당률 계산
    last_known_dividend = 0
    for i in range(len(new_stock_data)):
        if new_stock_data['Dividends'].iloc[i] > 0:
            last_known_dividend = new_stock_data['Dividends'].iloc[i]
        if last_known_dividend > 0:
            new_stock_data.loc[new_stock_data.index[i], 'Dividend Yield'] = (last_known_dividend / new_stock_data['Close'].iloc[i]) * 100

    # 마지막 5년치 데이터만 사용
    filtered_stock_data = new_stock_data[new_stock_data.index >= (current_date - pd.DateOffset(years=5))]

    # 5년 평균 배당 수익률 계산
    average_dividend_yield = filtered_stock_data['Dividend Yield'].mean()

    # Raw 데이터 출력 (주가, 배당, 시가배당률)
    print(filtered_stock_data.loc['2019-09-25':'2019-11-27', ['Close', 'Dividends', 'Dividend Yield']])

    # 차트 그리기
    plt.figure(figsize=(14, 10))

    # 주가 데이터 차트
    plt.subplot(3, 1, 1)
    plt.plot(filtered_stock_data.index, filtered_stock_data['Close'], label='Close Price')
    plt.title(f"{ticker_symbol} 5-year Stock Price")
    plt.ylabel('Price (KRW)' if nation_code == 'KOR' else 'Price (USD)')
    plt.legend()

    # 시가배당률 차트
    plt.subplot(3, 1, 2)
    plt.plot(filtered_stock_data.index, filtered_stock_data['Dividend Yield'], label='Dividend Yield', color='orange')
    plt.axhline(y=average_dividend_yield, color='red', linestyle='--', label='5-Year Avg Dividend Yield')
    plt.title(f"{ticker_symbol} Dividend Yield (5 years)")
    plt.ylabel('Dividend Yield (%)')
    plt.legend()

    plt.tight_layout()
    plt.show()



def main():
    # argparse 사용하여 명령줄 인수 처리
    parser = argparse.ArgumentParser(description="주식 종목명을 입력받습니다.")
    parser.add_argument('stock_name', type=str, help="검색할 종목명")
    
    # 명령줄 인수 파싱
    args = parser.parse_args()
        
    # 입력받은 종목명을 search_stock_code 함수로 전달
    r = search_stock_code(args.stock_name)

    # 검색 결과 로그 출력
    print("검색 결과:", r)

    # 종목 코드 찾기 로직 추가
    if len(r) == 1:
        # 검색 결과가 1개일 때, code와 nationCode를 get_ticker_symbol에 전달
        ticker_symbol = get_ticker_symbol(r[0]['code'], r[0]['nationCode'])
        
        if ticker_symbol:
            draw_dividend_yield_chart(ticker_symbol, r[0]['nationCode'])
        else:
            print("해당 종목의 종목 코드를 찾을 수 없습니다.")
            
    elif len(r) == 0:
        # 검색 결과가 없을 때
        print("해당 종목을 찾을 수 없습니다.")
        
    else:
        # 검색 결과가 여러 개일 때 사용자에게 선택하도록 하기
        print("여러 종목이 검색되었습니다. 선택해주세요:")
        
        for i, stock in enumerate(r):
            print(f"{i + 1}. {stock['name']} ({stock['typeName']}, {stock['nationName']})")
        
        choice = int(input("선택한 종목 번호를 입력하세요: ")) - 1
        
        if 0 <= choice < len(r):
            ticker_symbol = get_ticker_symbol(r[choice]['code'], r[choice]['nationCode'])
            
            if ticker_symbol:
                draw_dividend_yield_chart(ticker_symbol, r[choice]['nationCode'])
            else:
                print("해당 종목의 종목 코드를 찾을 수 없습니다.")
        else:
            print("잘못된 선택입니다.")
        
if __name__ == '__main__':
    main()