import requests, math, pandas as pd, concurrent.futures
from tqdm import tqdm
from config import HEADERS, MAX_WORKERS
from modules.naver_upjong_quant import fetch_stock_info_quant_API
from models.CacheManager import CacheManager
from config import CACHE_DB_PATH

cache_manager = CacheManager(str(CACHE_DB_PATH))

def fetch_all_stocks(base_url, market_name):
    first_url = base_url.format(page=1, page_size=100)
    response = requests.get(first_url, headers=HEADERS)
    if response.status_code != 200: return [], []
    total_count = response.json().get("totalCount", 0)
    total_pages = math.ceil(total_count / 100)
    all_stocks, etf_etn_stocks = [], []
    for page in range(1, total_pages + 1):
        page_url = base_url.format(page=page, page_size=100)
        res = requests.get(page_url, headers=HEADERS)
        if res.status_code == 200:
            for s in res.json().get("stocks", []):
                name = s.get("stockName", "")
                if '스팩' in name and '호' in name: continue
                raw_mv = str(s.get("marketValue", "0")).replace(",", "").strip()
                try:
                    mv = int(raw_mv) if raw_mv and raw_mv != "-" else 0
                except ValueError:
                    mv = 0
                info = {"종목코드": s.get("itemCode", ""), "종목명": name, "시가총액(억)": mv}
                if s.get("stockEndType") in ["etf", "etn"]: etf_etn_stocks.append(info)
                else: all_stocks.append(info)
    return all_stocks, etf_etn_stocks

def fetch_quant_data(stock_info, target_date=None):
    code = stock_info["종목코드"]
    cache_key = f"quant_{code}"
    
    cached = cache_manager.load_cache(cache_key)
    if cached and cache_manager.is_cache_valid(cache_key, "KOR"):
        return cached
    
    from app_secrets.endpoints import NAVER_STOCK_PAGE_URL
    url = NAVER_STOCK_PAGE_URL.format(stock_code=code, code=code)
    result = fetch_stock_info_quant_API(code, url=url, date=target_date) or {}
    
    if result:
        cache_manager.save_cache(cache_key, result, "KOR")
    
    return result

def add_quant_data(df, market_name, target_date=None):
    if df.empty: return df
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(fetch_quant_data, row, target_date) for row in df.to_dict('records')]
        results = [f.result() for f in tqdm(futures, desc=f"Quant {market_name}", leave=False)]
    
    df_res = pd.concat([df, pd.DataFrame(results)], axis=1)
    return df_res.sort_values(by="시가총액(억)", ascending=False).loc[:, ~df_res.columns.duplicated()]

def process_market_unit(market_tuple, target_date=None):
    market_name, base_url = market_tuple
    print(f"[{market_name}] 데이터 수집 시작... (기준일: {target_date or '오늘'})")
    stocks, etf_etn = fetch_all_stocks(base_url, market_name)
    df = add_quant_data(pd.DataFrame(stocks), market_name, target_date)
    return market_name, df, etf_etn
