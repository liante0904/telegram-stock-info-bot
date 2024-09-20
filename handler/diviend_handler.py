import os
import sys
from telegram import Update, InputFile
from telegram.ext import CallbackContext
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.naver_stock_quant import fetch_dividend_stock_list_API, save_stock_data_to_excel
from module.naver_stock_util import calculate_page_count
from module.excel_util import process_excel_file
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()  # .env 파일의 환경 변수를 로드합니다
today_date = datetime.today().strftime('%y%m%d')
async def send_dividend_stock_excel_quant(update: Update, context: CallbackContext) -> None:
    try:
        user_id = str(update.effective_user.id)
        user_input = update.message.text
        chat_id = update.effective_chat.id
        next_command = context.user_data.get('next_command')
        
        # API 호출하여 전체 배당 종목 수 가져오기
        # dividend_data = fetch_dividend_stock_list_API(page=1, pageSize=1)  # pageSize=1로 최소 데이터 호출
        # dividend_total_stock_count = dividend_data[0].get('totalCount', 0)

        # 사용자의 응답을 기다림
        user_message = user_input.strip()

        # 입력된 값이 숫자인지 확인
        if user_message.isdigit():
            requested_stock_count = int(user_message)
            # 페이지 수 계산 (1페이지당 100개 기준)
            page_count = calculate_page_count(requested_count=requested_stock_count)
        else:
            page_count = 0
            requested_stock_count = 0  # 숫자가 아닌 경우 전체 종목 전송

        # 입력된 종목 수가 전체 배당 종목 수 범위 내인지 확인
        if 1 <= requested_stock_count <= requested_stock_count:  # requested_stock_count를 기준으로 비교
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"*{requested_stock_count}*개의 종목을 전송합니다\\.",
                parse_mode='MarkdownV2'
            )
            print(f"요청된 종목 수: {requested_stock_count}, 페이지 수: {page_count}")
            # 수집된 데이터를 리스트에 추가
            all_data = fetch_dividend_stock_list_API(requested_stock_count=requested_stock_count)
            # 엑셀 파일로 저장
            excel_file_name = os.path.join(os.getenv('EXCEL_FOLDER_PATH'), f'dividend_naver_quant_{today_date}.xlsx')
            save_stock_data_to_excel(data=all_data, file_name=excel_file_name)
            # Send the file to the user
            if os.path.exists(excel_file_name):
                with open(excel_file_name, 'rb') as file:
                    await context.bot.send_document(chat_id=chat_id, document=InputFile(file, filename=os.path.basename(excel_file_name)))
        else:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"*전체 종목*을 전송합니다\\.",
                parse_mode='MarkdownV2'
            )
            print(f"전체 종목 전송: 페이지 수는 {page_count}")
            # 전체 종목 전송 로직 추가 (필요 시 함수 호출)
            all_data = fetch_dividend_stock_list_API(requested_stock_count=0)
            # 엑셀 파일로 저장
            excel_file_name = os.path.join(os.getenv('EXCEL_FOLDER_PATH'), f'dividend_naver_quant_{today_date}.xlsx')
            save_stock_data_to_excel(data=all_data, file_name=excel_file_name)

            # 엑셀 후처리 작업
            process_excel_file(excel_file_name)
            # Send the file to the user
            if os.path.exists(excel_file_name):
                with open(excel_file_name, 'rb') as file:
                    await context.bot.send_document(chat_id=chat_id, document=InputFile(file, filename=os.path.basename(excel_file_name)))
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"오류가 발생했습니다: {e}",
            parse_mode='MarkdownV2'
        )
