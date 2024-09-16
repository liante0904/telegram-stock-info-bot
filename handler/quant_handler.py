from telegram import Update, InputFile
from telegram.ext import CallbackContext
import os
import pandas as pd
from module.naver_upjong_quant import fetch_stock_info_quant_API
from datetime import datetime

async def process_selected_stock_for_quant(update: Update, context: CallbackContext, stock_name: str, stock_code: str, url: str):
    chat_id = update.effective_chat.id

    # 종목 정보를 가져옵니다.
    quant_data = fetch_stock_info_quant_API(stock_code, url)
    all_quant_data = []
    if quant_data:
        all_quant_data.append(quant_data)

    today_date = datetime.today().strftime('%y%m%d')
    excel_file_name = f'{stock_name}_naver_quant_{today_date}.xlsx'
    
    # Convert list of dictionaries to DataFrame
    if all_quant_data:
        df = pd.DataFrame(all_quant_data)
        df.to_excel(excel_file_name, index=False, engine='openpyxl')
        print(f'퀀트 정보가 {excel_file_name} 파일에 저장되었습니다.')

        if os.path.exists(excel_file_name):
            with open(excel_file_name, 'rb') as file:
                await context.bot.send_document(chat_id=chat_id, document=InputFile(file, filename=excel_file_name))
        else:
            await context.bot.send_message(chat_id=chat_id, text="엑셀 파일을 생성하는 데 문제가 발생했습니다.")
    else:
        await context.bot.send_message(chat_id=chat_id, text="퀀트 데이터를 가져오는 데 문제가 발생했습니다.")
