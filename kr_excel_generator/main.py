import sys, os, concurrent.futures, pandas as pd
from pathlib import Path
from datetime import datetime
from config import SEND_DIR, CACHE_DB_PATH
from data_fetcher import fetch_all_stocks, add_quant_data, process_market_unit
from excel_writer import save_to_excel
from telegram_sender import send_to_telegram

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.today().strftime('%y%m%d')
    ensure_directory(SEND_DIR)
    ensure_directory(CACHE_DB_PATH.parent)
    
    file_name = f"KR_stock_screening_{target_date}.xlsx"
    file_path = SEND_DIR / file_name
    
    if file_path.exists():
        file_path.unlink()
    
    print(f"🚀 [{target_date}] 병렬 수집 시작...")
    
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
    
    save_to_excel(market_dfs, df_etf, file_path)
    print(f"✅ [{target_date}] 엑셀 생성 완료 -> 전송")
    send_to_telegram(file_name, target_date)

if __name__ == '__main__':
    main()
