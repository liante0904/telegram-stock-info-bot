import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os

# 종목 설정 (예: AAPL)
ticker_symbol = "V"

# 캐시 파일 경로 설정
cache_filename = f"{ticker_symbol}_cache.csv"

def load_cache():
    if os.path.exists(cache_filename):
        print("=========================")
        return pd.read_csv(cache_filename, index_col=0, parse_dates=True)
    else:
        return None

def save_cache(dataframe):
    # CSV로 저장
    dataframe.to_csv(cache_filename)

# 현재 날짜를 가져오기
current_date = pd.Timestamp.now()

# 캐시 데이터 로드
cached_data = load_cache()

# 캐시 데이터가 있으면 범위 내 날짜 데이터 추출
if cached_data is not None:
    # 캐시된 데이터의 마지막 날짜
    cached_data_end_date = cached_data.index.max()
    # 필요한 데이터 범위
    if cached_data_end_date > (current_date - pd.DateOffset(years=5)):
        stock_data = cached_data[cached_data.index >= (current_date - pd.DateOffset(years=5))]
    else:
        # 캐시 데이터가 5년 이내에 없으면 빈 데이터 프레임 생성
        stock_data = pd.DataFrame()
else:
    stock_data = pd.DataFrame()

if stock_data.empty or stock_data.index.max() < (current_date - pd.DateOffset(days=1)):
    # yfinance에서 주식 데이터 다운로드 (5년 데이터)
    ticker = yf.Ticker(ticker_symbol)
    # 5년치 주가 및 배당금 데이터 가져오기
    new_stock_data = ticker.history(period="5y")
    dividends = ticker.dividends

    # 타임존 문제 해결: tz-aware를 tz-naive로 변경
    new_stock_data.index = new_stock_data.index.tz_localize(None)
    dividends.index = dividends.index.tz_localize(None)

    # 배당 정보가 없는 일자를 제외하고 주가 데이터와 병합
    new_stock_data['Dividends'] = dividends.reindex(new_stock_data.index, fill_value=0)

    # 시가배당률 계산: (배당금 / 종가) * 100
    new_stock_data['Dividend Yield'] = (new_stock_data['Dividends'] / new_stock_data['Close']) * 100

    # 직전 배당금 기록
    last_known_dividend = 0

    # 3개월 기준 기간 설정
    three_months_delta = pd.DateOffset(months=3)

    # 배당금 없는 날에 대해 처리
    for i in range(len(new_stock_data)):
        if new_stock_data['Dividends'].iloc[i] > 0:
            # 배당금이 있는 경우, 직전 배당금 업데이트
            last_known_dividend = new_stock_data['Dividends'].iloc[i]
            new_stock_data.loc[new_stock_data.index[i], 'Dividend Yield'] = (last_known_dividend / new_stock_data['Close'].iloc[i]) * 100
        else:
            # 배당금이 없는 경우
            if new_stock_data.index[i] > current_date:
                # 미래 날짜는 처리하지 않음
                continue

            # 3개월 이내의 배당금 이력 확인
            recent_dividends = new_stock_data[(new_stock_data.index < new_stock_data.index[i]) & 
                                              (new_stock_data.index >= new_stock_data.index[i] - three_months_delta) & 
                                              (new_stock_data['Dividends'] > 0)]

            if not recent_dividends.empty:
                # 3개월 이내에 배당이 있다면 그 값으로 배당률 계산
                last_known_dividend = recent_dividends['Dividends'].iloc[-1]
            else:
                # 3개월 이내에 배당이 없으면, 그 이전의 배당금 이력 가져오기
                past_dividends = new_stock_data[(new_stock_data.index < new_stock_data.index[i] - three_months_delta) & 
                                                (new_stock_data['Dividends'] > 0)]
                if not past_dividends.empty:
                    last_known_dividend = past_dividends['Dividends'].iloc[-1]
                else:
                    # 배당금 이력이 없으면 0%로 처리
                    last_known_dividend = 0

            # 시가배당률 계산
            new_stock_data.loc[new_stock_data.index[i], 'Dividends'] = last_known_dividend
            if last_known_dividend > 0:
                new_stock_data.loc[new_stock_data.index[i], 'Dividend Yield'] = (last_known_dividend / new_stock_data['Close'].iloc[i]) * 100
            else:
                new_stock_data.loc[new_stock_data.index[i], 'Dividend Yield'] = 0

    # 기존 캐시와 새 데이터를 병합
    if not stock_data.empty:
        stock_data = pd.concat([stock_data, new_stock_data]).drop_duplicates().sort_index()
    else:
        stock_data = new_stock_data

    # 캐시 업데이트
    save_cache(stock_data)

# 5년 평균 배당 수익률 계산
average_dividend_yield = stock_data['Dividend Yield'].mean()

# Raw 데이터 출력 (주가, 배당, 시가배당률)
print(stock_data.head())  # 처음 5개 행만 출력 (원하는 만큼 수정 가능)

# 차트 그리기
plt.figure(figsize=(14, 10))

# 주가 데이터 차트
plt.subplot(3, 1, 1)
plt.plot(stock_data.index, stock_data['Close'], label='Close Price')
plt.title(f"{ticker_symbol} 5-year Stock Price")
plt.ylabel('Price (USD)')
plt.legend()

# 시가배당률 차트
plt.subplot(3, 1, 2)
plt.plot(stock_data.index, stock_data['Dividend Yield'], label='Dividend Yield', color='orange')
plt.axhline(y=average_dividend_yield, color='red', linestyle='--', label='5-Year Avg Dividend Yield')
plt.title(f"{ticker_symbol} Dividend Yield (5 years)")
plt.ylabel('Dividend Yield (%)')
plt.legend()

plt.tight_layout()
plt.show()
