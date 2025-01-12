from telegram.ext import CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.oscillator_chart import draw_chart
from utils.recent_search_util import save_recent_searches
from utils.naver_stock_util import search_stock_code

async def process_selected_stock_for_chart(update: Update, context: CallbackContext, stock_name: str, stock_code: str):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    
    await update.callback_query.message.reply_text(f"{stock_name}({stock_code}) 차트를 생성 중...")

    # 최근 검색 종목에 추가 (중복 방지)
    if user_id not in context.bot_data['recent_searches']:
        context.bot_data['recent_searches'][user_id] = []
    if not any(search['name'] == stock_name for search in context.bot_data['recent_searches'][user_id]):
        context.bot_data['recent_searches'][user_id].append({'name': stock_name, 'code': stock_code})
    save_recent_searches(context.bot_data['recent_searches'])

    chart_filename = draw_chart(stock_code, stock_name)
    if os.path.exists(chart_filename):
        context.user_data['generated_charts'].append(chart_filename)
    else:
        await update.callback_query.message.reply_text(f"차트 파일을 찾을 수 없습니다: {chart_filename}")

    # 나머지 종목 처리
    remaining_stocks = context.user_data.get('remaining_stocks', [])
    if remaining_stocks:
        context.user_data['stock_list'] = remaining_stocks
        await process_generate_chart_stock_list(update, context, user_id, update.callback_query.message)
    else:
        # 미디어 그룹을 한 번만 전송
        await generate_and_send_charts_from_files(context, chat_id, context.user_data['generated_charts'])

        # 모든 차트 생성 후 상태 재설정
        context.user_data['next_command'] = None
        await context.bot.send_message(chat_id=update.effective_chat.id, text='모든 차트를 전송했습니다. 다른 종목을 검색하시려면 종목명을 입력해주세요.')
        context.user_data['next_command'] = 'generate_chart'  # 상태 재설정

async def generate_and_send_charts_from_files(context, chat_id, chart_files):
    media_groups = []
    current_group = []
    files_to_close = []

    for chart_filename in chart_files:
        file = open(chart_filename, 'rb')
        files_to_close.append(file)
        if len(current_group) < 10:
            current_group.append(InputMediaPhoto(file, filename=chart_filename))
        else:
            media_groups.append(current_group)
            current_group = [InputMediaPhoto(file, filename=chart_filename)]

    if current_group:
        media_groups.append(current_group)

    for group in media_groups:
        await context.bot.send_media_group(chat_id=chat_id, media=group)
    
    for file in files_to_close:
        file.close()

async def process_generate_chart_stock_list(update: Update, context: CallbackContext, user_id: str, message) -> None:
    stock_list = context.user_data.get('stock_list', [])

    for stock_name in stock_list:
        results = search_stock_code(stock_name)
        if results and len(results) == 1:
            stock_name, stock_code = results[0]['name'], results[0]['code']
            await message.reply_text(f"{stock_name}({stock_code}) 차트를 생성 중...")

            # 최근 검색 종목에 추가 (중복 방지)
            if user_id not in context.bot_data['recent_searches']:
                context.bot_data['recent_searches'][user_id] = []
            if not any(search['name'] == stock_name for search in context.bot_data['recent_searches'][user_id]):
                context.bot_data['recent_searches'][user_id].append({'name': stock_name, 'code': stock_code})
            save_recent_searches(context.bot_data['recent_searches'])

            chart_filename = draw_chart(stock_code, stock_name)
            if os.path.exists(chart_filename):
                context.user_data['generated_charts'].append(chart_filename)
            else:
                await message.reply_text(f"차트 파일을 찾을 수 없습니다: {chart_filename}")

        elif results and len(results) > 1:
            buttons = [[InlineKeyboardButton(f"{result['name']} ({result['code']})", callback_data=result['code'])] for result in results]
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply_text("검색 결과를 선택하세요:", reply_markup=reply_markup)
            context.user_data['search_results'] = results
            context.user_data['remaining_stocks'] = stock_list[stock_list.index(stock_name) + 1:]
            return
        else:
            await message.reply_text(f"{stock_name} 검색 결과가 없습니다. 다시 시도하세요.")

    # 미디어 그룹을 한 번만 전송
    await generate_and_send_charts_from_files(context, update.effective_chat.id, context.user_data['generated_charts'])

    # 모든 차트 생성 후 상태 재설정
    context.user_data['next_command'] = None
    await context.bot.send_message(chat_id=update.effective_chat.id, text='모든 차트를 전송했습니다. 다른 종목을 검색하시려면 종목명을 입력해주세요.')
    context.user_data['next_command'] = 'generate_chart'  # 상태 재설정
  