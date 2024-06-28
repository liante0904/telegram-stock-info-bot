import numpy as np
import pandas as pd
from pykrx import stock
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# 시스템 일자 읽기 (오늘 날짜)
today = datetime.today()
today_str = today.strftime('%Y%m%d')

# 120 거래일 전 날짜 계산
start_date = today - timedelta(days=180)  # 주말과 공휴일을 고려하여 여유롭게 180일로 설정
start_date_str = start_date.strftime('%Y%m%d')

# KOSPI 종목별 시가총액 데이터 가져오기
tickers = stock.get_market_ticker_list(market="KOSPI")
data = []

# 업종 정보를 가져오는 방법
sector_info = stock.get_market_ticker_name(tickers)  # 모든 종목에 대한 이름 정보

for ticker in tickers:
    name = stock.get_market_ticker_name(ticker)
    # 120 거래일 범위 내의 시가총액 데이터 가져오기
    market_cap_data = stock.get_market_cap_by_date(start_date_str, today_str, ticker)
    if not market_cap_data.empty:
        # 마지막 거래일의 시가총액 사용
        market_cap = market_cap_data['시가총액'].values[-1]
        # 업종 정보 수집 (종목 이름을 통해 업종 정보를 구함)
        sector = sector_info.get(ticker)
        data.append([name, sector, market_cap])

# 데이터프레임 생성
df = pd.DataFrame(data, columns=['Name', 'Sector', 'MarketCap'])

# 업종별 시가총액 계산
sector_market_cap = df.groupby('Sector')['MarketCap'].sum()

# 전체 시가총액 계산
total_market_cap = sector_market_cap.sum()

# 각 업종의 시장 점유율 계산
market_shares = sector_market_cap / total_market_cap

# HHI 계산
hhi = sum((share ** 2) for share in market_shares)

print(f'허핀달-허시만 지수 (HHI): {hhi:.4f}')

# 업종별 시가총액을 리스트로 변환 (차트 생성을 위해)
sector_market_cap_values = sector_market_cap.values
labels = sector_market_cap.index

# 파이차트 생성
plt.figure(figsize=(10, 7))
plt.pie(sector_market_cap_values, labels=labels, autopct='%1.1f%%', startangle=140)
plt.title('업종별 시가총액 분포 (KOSPI) - 최근 120 거래일 기준')
plt.savefig()

# 시가총액 데이터를 저장하여 MATLAB로 전달
np.savetxt('market_shares.txt', market_shares.values)
