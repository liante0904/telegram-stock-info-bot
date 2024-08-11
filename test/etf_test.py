from pykrx import stock
import sys
import os

# 현재 파일(test.py)의 디렉토리 기준으로 상대 경로를 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../module')

# stock_search 모듈을 임포트
from stock_search import search_stock


# ETF 포트폴리오 데이터를 가져옴
df = stock.get_etf_portfolio_deposit_file("449450")
# print(df.head())

# 종목명을 가져오는 함수 정의
def get_stock_name(ticker):
    result = search_stock(ticker)
    # 종목명 추출
    if result and len(result) > 0:
        return result[0]['name']
    return 'Unknown'

# 종목명을 저장할 새로운 열을 추가
df['종목명'] = [get_stock_name(ticker) for ticker in df.index]

# 티커를 인덱스에서 열로 변환
df.reset_index(inplace=True)

# 열 순서를 재정렬 (티커, 종목명, 계약수, 금액, 비중)
df = df[['티커', '종목명', '계약수', '금액', '비중']]

# 데이터프레임의 행 수와 내용 확인
print(f"전체 데이터프레임의 행 수 (종목명 추가 후): {len(df)}")
print("데이터프레임의 처음 몇 행:")
print(df)
