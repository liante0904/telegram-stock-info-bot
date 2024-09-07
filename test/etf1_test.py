from pykrx import stock
from cachetools import TTLCache, cached

# 하루 동안 캐시 유지 (60초 * 60분 * 24시간 = 86400초)
cache = TTLCache(maxsize=1, ttl=86400)

@cached(cache)
def get_etf_tickers():
    return stock.get_etf_ticker_list()

# 프로그램 시작 시 ETF 데이터를 미리 캐싱
get_etf_tickers()

def is_etf(ticker):
    etf_tickers = get_etf_tickers()
    return ticker in etf_tickers

# 예시 사용법
ticker = "069500"  # KODEX 200 ETF 종목 코드

# 이미 캐시가 된 후의 첫 번째 호출
import time
start_time = time.time()
if is_etf(ticker):
    print(f"{ticker}는 ETF입니다.")
else:
    print(f"{ticker}는 ETF가 아닙니다.")
print(f"첫 번째 호출에 걸린 시간: {time.time() - start_time}초")

# 두 번째 호출 (캐시된 결과 사용)
start_time = time.time()
if is_etf(ticker):
    print(f"{ticker}는 ETF입니다.")
else:
    print(f"{ticker}는 ETF가 아닙니다.")
print(f"두 번째 호출에 걸린 시간: {time.time() - start_time}초")
