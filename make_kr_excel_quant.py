import random, time, os, requests, pandas as pd, math, concurrent.futures, sys
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
from datetime import datetime
from modules.naver_upjong_quant import fetch_stock_info_quant_API

# 전역 설정
kospi_url = "https://m.stock.naver.com/api/stocks/marketValue/KOSPI"
kosdaq_url = "https://m.stock.naver.com/api/stocks/marketValue/KOSDAQ"
max_workers = 4 
headers = {"User-Agent": "Mozilla/5.0"}

def ensure_directory(path):
    if not os.path.exists(path): os.makedirs(path, exist_ok=True)

def fetch_all_stocks(base_url, market_name):
    params = {"page": 1, "pageSize": 100}
    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code != 200: return [], []
    total_count = response.json().get("totalCount", 0)
    total_pages = math.ceil(total_count / 100)
    all_stocks, etf_etn_stocks = [], []
    for page in range(1, total_pages + 1):
        res = requests.get(base_url, headers=headers, params={"page": page, "pageSize": 100})
        if res.status_code == 200:
            for s in res.json().get("stocks", []):
                name = s.get("stockName", "")
                if '스팩' in name and '호' in name: continue
                info = {"종목코드": s.get("itemCode", ""), "종목명": name, "시가총액(억)": int(str(s.get("marketValue", "0")).replace(",", ""))}
                if s.get("stockEndType") in ["etf", "etn"]: etf_etn_stocks.append(info)
                else: all_stocks.append(info)
    return all_stocks, etf_etn_stocks

def fetch_quant_data(stock_info, target_date=None):
    code = stock_info["종목코드"]
    url = f"https://m.stock.naver.com/item/main.nhn#/stocks/{code}/total"
    # 날짜 인자를 추가하여 API 호출
    return fetch_stock_info_quant_API(code, url=url, date=target_date) or {}

def add_quant_data(df, market_name, target_date=None):
    if df.empty: return df
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # target_date를 각 스레드에 전달
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

def send_to_telegram(file_name, target_date):
    BASE_DIR = Path(__file__).parent.resolve()
    load_dotenv(dotenv_path=BASE_DIR / ".env")
    FILE_PATH = BASE_DIR / "send" / file_name
    if not os.path.exists(FILE_PATH): return False
    token = os.getenv('TELEGRAM_BOT_TOKEN_PROD')
    chat_id = os.getenv('TELEGRAM_CHANNEL_ID_REPORT_ALARM')
    if not token or not chat_id: return False
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    caption = f"📊 [{target_date}] 주식 스크리닝 결과"
    with open(FILE_PATH, 'rb') as f:
        res = requests.post(url, data={'chat_id': chat_id, 'caption': caption}, files={'document': f})
    return res.status_code == 200

def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.today().strftime('%y%m%d')
    BASE_DIR = Path(__file__).parent.resolve()
    send_dir = BASE_DIR / "send"
    ensure_directory(send_dir)
    file_name = f"KR_stock_screening_{target_date}.xlsx"
    file_path = send_dir / file_name

    # 과거 날짜 작업 시 기존 파일이 있으면 덮어쓰기 위해 삭제
    if os.path.exists(file_path):
        try: os.remove(file_path)
        except: pass

    print(f"🚀 [{target_date}] 병렬 수집 및 실시간 수익률 계산 시작...")
    markets_to_process = [("KOSPI", kospi_url), ("KOSDAQ", kosdaq_url)]
    
    market_dfs = {}
    combined_etf_etn = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(process_market_unit, m, target_date) for m in markets_to_process]
        for future in concurrent.futures.as_completed(futures):
            name, df, etf_list = future.result()
            market_dfs[name] = df
            combined_etf_etn.extend(etf_list)

    print("[ETF_ETN] 데이터 수집 시작...")
    df_etf = add_quant_data(pd.DataFrame(combined_etf_etn), "ETF_ETN", target_date)

    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
        if "KOSPI" in market_dfs: market_dfs["KOSPI"].to_excel(writer, sheet_name="KOSPI", index=False)
        if "KOSDAQ" in market_dfs: market_dfs["KOSDAQ"].to_excel(writer, sheet_name="KOSDAQ", index=False)
        df_etf.to_excel(writer, sheet_name="ETF_ETN", index=False)
        for sheet in writer.sheets.values():
            sheet.set_column(1, 1, 25)
            sheet.freeze_panes(1, 0)
    
    print(f"✅ [{target_date}] 엑셀 생성 완료 -> 전송")
    send_to_telegram(file_name, target_date)

if __name__ == '__main__':
    main()
