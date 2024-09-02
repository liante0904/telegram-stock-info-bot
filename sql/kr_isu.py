import sqlite3
import os
import argparse
import sys
from datetime import datetime

# 현재 스크립트의 상위 디렉터리를 모듈 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from module.pykrx_util import get_all_tickers_and_names

# 데이터베이스 파일 경로
db_path = os.path.expanduser('~/sqlite3/telegram.db')

# SQLite 데이터베이스 연결
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 명령행 인자 파서 설정
parser = argparse.ArgumentParser(description="SQLite STOCK_INFO_MASTER_KR_ISU Table Management Script")
parser.add_argument('action', choices=['create', 'insert', 'select', 'update', 'delete'], help="Action to perform")
parser.add_argument('isu', nargs='?', help="6자리 종목 코드 또는 종목명")  # 종목 코드 또는 이름을 받음
parser.add_argument('--market', help="시장 종류 (KOSPI, KOSDAQ)")
parser.add_argument('--sector', help="업종")
parser.add_argument('--date', help="조회할 날짜 (YYYYMMDD, YYMMDD, YYYY-MM-DD)")
args = parser.parse_args()

def select_data(isu=None, date=None):
    """STOCK_INFO_MASTER_KR_ISU 테이블에서 데이터를 조회합니다."""
    query = "SELECT ISU_NO, ISU_NM, MARKET, SECTOR, LAST_UPDATED FROM STOCK_INFO_MASTER_KR_ISU WHERE 1=1"
    params = []

    if isu:
        query += " AND (ISU_NO = ? OR ISU_NM = ?)"  # ISU_NO 또는 ISU_NM으로 검색
        params.extend([isu, isu])  # 같은 값이므로 두 번 추가
    
    # date 필터링은 주석처리 되었으므로 제거했습니다.
    
    cursor.execute(query, params)
    results = cursor.fetchall()

    # 컬럼명 가져오기
    column_names = [description[0] for description in cursor.description]

    # 데이터 출력
    print("\nFetched Data:")
    print(f"{' | '.join(column_names)}")  # 컬럼명 출력
    if results:
        for row in results:
            print(' | '.join(str(item) if item is not None else 'None' for item in row))
    else:
        print("No data found.")
        
def create_table():
    """STOCK_INFO_MASTER_KR_ISU 테이블을 생성합니다."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS STOCK_INFO_MASTER_KR_ISU (
            ISU_NO TEXT(6) PRIMARY KEY,      -- 6자리 종목 코드
            ISU_NM TEXT(40) NOT NULL,        -- 40자리 종목명
            MARKET TEXT NOT NULL,            -- 시장 종류 (KOSPI, KOSDAQ)
            SECTOR TEXT,                     -- 업종
            LAST_UPDATED DATETIME DEFAULT CURRENT_TIMESTAMP  -- 마지막 업데이트 시점
        )
    """)
    conn.commit()
    print("Table STOCK_INFO_MASTER_KR_ISU created successfully.")

def insert_all_data():
    """모든 종목 데이터를 STOCK_INFO_MASTER_KR_ISU 테이블에 삽입합니다."""
    tickers = get_all_tickers_and_names()
    for market, data in tickers.items():
        for isu_no, isu_nm in data.items():
            cursor.execute("""
                INSERT INTO STOCK_INFO_MASTER_KR_ISU (ISU_NO, ISU_NM, MARKET) 
                VALUES (?, ?, ?)
                ON CONFLICT(ISU_NO) DO UPDATE SET
                ISU_NM = excluded.ISU_NM,
                MARKET = excluded.MARKET,
                LAST_UPDATED = CURRENT_TIMESTAMP
            """, (isu_no, isu_nm, market))
    conn.commit()
    print("All data inserted successfully.")

def update_data(isu_no, isu_nm=None, market=None, sector=None):
    """STOCK_INFO_MASTER_KR_ISU 테이블의 데이터를 업데이트합니다."""
    if not isu_no:
        raise ValueError("ISU_NO is required for update operation.")

    updates = []
    params = []

    if isu_nm:
        updates.append("ISU_NM = ?")
        params.append(isu_nm)
    if market:
        updates.append("MARKET = ?")
        params.append(market)
    if sector:
        updates.append("SECTOR = ?")
        params.append(sector)

    params.append(isu_no)

    if not updates:
        print("No fields to update.")
        return

    query = f"UPDATE STOCK_INFO_MASTER_KR_ISU SET {', '.join(updates)}, LAST_UPDATED = CURRENT_TIMESTAMP WHERE ISU_NO = ?"
    cursor.execute(query, params)
    conn.commit()
    print(f"Data updated for ISU_NO: {isu_no}")

def delete_data(isu_no):
    """STOCK_INFO_MASTER_KR_ISU 테이블에서 데이터를 삭제합니다."""
    cursor.execute("DELETE FROM STOCK_INFO_MASTER_KR_ISU WHERE ISU_NO = ?", (isu_no,))
    conn.commit()
    print(f"Data deleted for ISU_NO: {isu_no}")

if __name__ == "__main__":
    if args.action == 'create':
        create_table()
    elif args.action == 'insert':
        insert_all_data()  # 전체 종목을 삽입
    elif args.action == 'select':
        select_data(args.isu, args.date)  # ISU_NO 또는 ISU_NM을 받을 수 있음
    elif args.action == 'update':
        if not args.isu:
            raise ValueError("ISU_NO is required for update operation.")
        update_data(args.isu, args.market, args.sector)
    elif args.action == 'delete':
        if not args.isu:
            raise ValueError("ISU_NO is required for delete operation.")
        delete_data(args.isu)

    conn.close()
