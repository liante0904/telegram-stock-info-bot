from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import os
import asyncio
import re
import json
from dotenv import load_dotenv
from module.stock_search import search_stock
from module.chart import draw_chart, CHART_DIR
from module.recent_searches import load_recent_searches, save_recent_searches, show_recent_searches
from handler.report_handler import process_report_request, previous_search, select_stock, fetch_and_send_reports
from handler.chart_handler import generate_and_send_charts_from_files
from datetime import datetime, timedelta


# JSON 파일 경로
KEYWORD_FILE_PATH = 'report_alert_keyword.json'

async def chart(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text='수급오실레이터 차트 생성입니다. \n\n 종목명 혹은 종목코드를 입력하세요. \n 쉼표(,) 혹은 여러줄로 입력하면 다중생성이 가능합니다. \n 종목코드로 입력시 더 빠름')
    context.user_data['next_command'] = 'generate_chart'

async def report(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text='레포트를 검색할 종목명을 입력하세요.')
    context.user_data['next_command'] = 'search_report'


async def report_alert_keyword(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    
    # 현재 저장된 키워드 로드
    all_keywords = load_keywords()
    current_keywords = [keyword['keyword'] for keyword in all_keywords.get(user_id, [])]

    # 사용자에게 현재 저장된 키워드를 보여주고 입력 요청
    if current_keywords:
        keyword_text = '\n'.join([f"- {keyword}" for keyword in current_keywords])
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"현재 저장된 알림 키워드:\n{keyword_text}\n\n새로운 키워드를 쉼표(,) 또는 하이픈(-)으로 구분하여 입력해주세요."
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text='현재 저장된 알림 키워드가 없습니다. \n\n 새로운 키워드를 쉼표(,) 또는 하이픈(-)으로 구분하여 입력해주세요.'
        )

    # 다음 명령어 상태 설정
    context.user_data['next_command'] = 'report_alert_keyword'

# JSON 파일에서 사용자 알림 키워드를 불러오는 함수
def load_keywords():
    if os.path.exists(KEYWORD_FILE_PATH):
        with open(KEYWORD_FILE_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# JSON 파일에 사용자 알림 키워드를 저장하는 함수
def save_keywords(keywords):
    with open(KEYWORD_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(keywords, file, ensure_ascii=False, indent=4)


async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    next_command = context.user_data.get('next_command')

    if next_command == 'report_alert_keyword':
        user_input = update.message.text
        # 쉼표와 하이픈을 구분자로 사용하여 입력 처리
        keywords = [keyword.strip() for keyword in re.split('[,-]', user_input) if keyword.strip()]

        # 중복 제거를 위해 set 사용
        unique_keywords = set(keywords)

        # 현재 저장된 키워드 로드 및 중복 제거
        all_keywords = load_keywords()
        if user_id not in all_keywords:
            all_keywords[user_id] = []

        # 기존 키워드에서 중복 제거
        existing_keywords = {entry['keyword'] for entry in all_keywords.get(user_id, [])}
        new_keywords = [{'keyword': keyword, 'code': '', 'timestamp': datetime.now().isoformat()} for keyword in unique_keywords if keyword not in existing_keywords]

        # 사용자 알림 키워드 업데이트
        all_keywords[user_id].extend(new_keywords)
        # 각 사용자별로 중복 키워드 제거
        unique_user_keywords = {}
        for entry in all_keywords[user_id]:
            unique_user_keywords[entry['keyword']] = entry
        all_keywords[user_id] = list(unique_user_keywords.values())

        save_keywords(all_keywords)


        # 상태 초기화 및 확인 메시지 전송
        context.user_data['next_command'] = None
        updated_keywords = [keyword['keyword'] for keyword in all_keywords[user_id]]
        updated_keywords_text = '\n'.join([f"- {keyword}" for keyword in updated_keywords])
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"키워드 알림이 설정되었습니다.\n\n현재 저장된 알림 키워드:\n{updated_keywords_text}"
        )
    elif next_command == 'generate_chart':
        user_input = update.message.text
        stock_list = [stock.strip() for stock in re.split('[,\n]', user_input) if stock.strip()]
        context.user_data['stock_list'] = stock_list
        context.user_data['generated_charts'] = []
        await process_stock_list(update, context, user_id, update.message)

    elif next_command == 'search_report':
        user_input = update.message.text
        stock_list = [stock.strip() for stock in re.split('[,\n]', user_input) if stock.strip()]
        context.user_data['stock_list'] = stock_list
        context.user_data['writeFromDate'] = (datetime.today() - timedelta(days=14)).strftime('%Y-%m-%d')
        context.user_data['writeToDate'] = datetime.today().strftime('%Y-%m-%d')
        await process_report_request(update, context, user_id, update.message)

async def process_stock_list(update: Update, context: CallbackContext, user_id: str, message) -> None:
    stock_list = context.user_data.get('stock_list', [])
    remaining_stocks = []

    for stock_name in stock_list:
        results = search_stock(stock_name)
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

async def generate_and_send_charts_from_files(context: CallbackContext, chat_id, chart_files):
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

async def select_stock(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    selected_code = query.data
    results = context.user_data.get('search_results', [])
    next_command = context.user_data.get('next_command')

    for result in results:
        if result['code'] == selected_code:
            stock_name, stock_code = result['name'], result['code']
            if next_command == 'generate_chart':
                await process_selected_stock_for_chart(update, context, stock_name, stock_code)
            elif next_command == 'search_report':
                await process_selected_stock_for_report(update, context, stock_name, stock_code)

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
        await process_stock_list(update, context, user_id, update.callback_query.message)
    else:
        # 미디어 그룹을 한 번만 전송
        await generate_and_send_charts_from_files(context, chat_id, context.user_data['generated_charts'])

        # 모든 차트 생성 후 상태 재설정
        context.user_data['next_command'] = None
        await context.bot.send_message(chat_id=update.effective_chat.id, text='모든 차트를 전송했습니다. 다른 종목을 검색하시려면 종목명을 입력해주세요.')
        context.user_data['next_command'] = 'generate_chart'  # 상태 재설정

async def process_selected_stock_for_report(update: Update, context: CallbackContext, stock_name: str, stock_code: str):
    context.user_data['writeFromDate'] = context.user_data.get('writeFromDate', (datetime.today() - timedelta(days=14)).strftime('%Y-%m-%d'))
    context.user_data['writeToDate'] = datetime.today().strftime('%Y-%m-%d')
    await fetch_and_send_reports(update, context, str(update.callback_query.from_user.id), update.callback_query.message, stock_name, stock_code, context.user_data['writeFromDate'], context.user_data['writeToDate'])

    # 나머지 종목 처리
    remaining_stocks = context.user_data.get('remaining_stocks', [])
    if remaining_stocks:
        context.user_data['stock_list'] = remaining_stocks
        await process_report_request(update, context, str(update.callback_query.from_user.id), update.callback_query.message)

async def set_commands(bot):
    commands = [
        BotCommand("chart", "수급오실레이터 차트"),
        BotCommand("recent", "최근 검색 종목"),
        BotCommand("report", "레포트 검색기"),
        BotCommand("report_alert_keyword", "레포트 알림 키워드 설정")  # 추가된 명령어
    ]
    await bot.set_my_commands(commands)

def main():
    
    load_dotenv()  # .env 파일의 환경 변수를 로드합니다
    env = os.getenv('ENV')
    print(env)
    if env == 'production':
        token = os.getenv('TELEGRAM_BOT_TOKEN_PROD')
    else:
        token = os.getenv('TELEGRAM_BOT_TOKEN_TEST')


    application = ApplicationBuilder().token(token).build()

    recent_searches = load_recent_searches()
    application.bot_data['recent_searches'] = recent_searches

    application.add_handler(CommandHandler("chart", chart))  # /chart 명령어 추가
    application.add_handler(CommandHandler("recent", show_recent_searches))  # 최근 검색 종목 명령어 추가
    application.add_handler(CommandHandler("report", report))  # 레포트 검색기 명령어 추가
    application.add_handler(CommandHandler("report_alert_keyword", report_alert_keyword))  # 알림 키워드 명령어 추가
    application.add_handler(CallbackQueryHandler(select_stock, pattern=r'^\d{6}$'))
    application.add_handler(CallbackQueryHandler(previous_search, pattern='^previous_search$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # asyncio 이벤트 루프에서 명령어 설정
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_commands(application.bot))

    application.run_polling()

if __name__ == '__main__':
    if not os.path.exists(CHART_DIR):
        os.makedirs(CHART_DIR)
    main()
