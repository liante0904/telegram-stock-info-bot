import os
import sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font
# 현재 스크립트의 상위 디렉터리를 모듈 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from module.naver_upjong_quant import fetch_upjong_list_API, fetch_stock_info_in_upjong, fetch_stock_info_quant_API
from datetime import datetime

# Define the folder path
EXCEL_FOLDER_PATH = 'excel/'  # Adjust this to your actual folder path if needed

# 업종 검색 처리
upjong_list = fetch_upjong_list_API()
upjong_map = {업종명: (등락률, 링크) for 업종명, 등락률, 링크 in upjong_list}

# Ensure the folder exists
if not os.path.exists(EXCEL_FOLDER_PATH):
    os.makedirs(EXCEL_FOLDER_PATH)
    
today_date = datetime.today().strftime('%y%m%d')
# 엑셀 파일명 생성 (하나의 파일에 업종별 시트를 누적 저장)
excel_file_name = os.path.join(EXCEL_FOLDER_PATH, f'네이버전체업종_naver_quant_{today_date}.xlsx')

# 새 엑셀 파일 생성
wb = Workbook()
wb.remove(wb.active)  # 기본으로 생성된 시트 제거

# 모든 업종에 대해 처리
for 업종명, (등락률, 링크) in upjong_map.items():
    print(f"=================업종명: {업종명}, 등락률: {등락률}=================")
    if 업종명 == '기타':  # ETN & ETF는 건너뛰기
        continue

    stock_info = fetch_stock_info_in_upjong(링크)

    if stock_info:
        all_quant_data = []
        for 종목명, _, _, _, 종목링크 in stock_info:
            stock_code = 종목링크.split('=')[-1]
            quant_data = fetch_stock_info_quant_API(stock_code)
            if quant_data:
                all_quant_data.append(quant_data)
            else:
                pass

        if all_quant_data:
            # Create a DataFrame and save to Excel with the sheet name as 업종명
            df = pd.DataFrame(all_quant_data)
            ws = wb.create_sheet(title=업종명)  # 새 시트 생성

            # 데이터프레임을 시트에 작성
            for row in dataframe_to_rows(df, index=False, header=True):
                ws.append(row)

            # 필터 기능 추가 및 하이퍼링크 처리
            start_row, start_col = 1, 1
            end_row = ws.max_row  # 실제 데이터가 있는 마지막 행을 가져옴
            end_col = ws.max_column  # 실제 데이터가 있는 마지막 열을 가져옴
            cell_range = f'{get_column_letter(start_col)}{start_row}:{get_column_letter(end_col)}{end_row}'
            ws.auto_filter.ref = cell_range  # 필터 범위 지정

            # '네이버url' 열의 하이퍼링크 처리
            if '네이버url' in df.columns:
                nav_url_col_index = df.columns.get_loc('네이버url') + 1  # 1-based index
                for row in ws.iter_rows(min_row=2, max_row=end_row, min_col=nav_url_col_index, max_col=nav_url_col_index):
                    for cell in row:
                        if cell.value:
                            cell.hyperlink = cell.value
                            cell.font = Font(color="0000FF", underline="single")

# 엑셀 파일 저장
wb.save(excel_file_name)
wb.close()

print(f'업종별 퀀트 정보가 {excel_file_name} 파일에 저장되었습니다.')
