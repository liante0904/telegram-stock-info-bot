from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import os
from package.SecretKey import SecretKey
from stock_search import search_stock
from chart import draw_chart

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text='안녕하세요! 주식 차트 생성 봇입니다. 차트를 생성할 주식의 종목명을 입력하세요.')
    context.user_data['next_command'] = 'generate_chart'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'next_command' in context.user_data and context.user_data['next_command'] == 'generate_chart':
        user_input = update.message.text
        results = search_stock(user_input)
        
        if results:
            if len(results) == 1:
                stock_name, stock_code = results[0]['name'], results[0]['code']
                await update.message.reply_text(f"{stock_name} ({stock_code})에 대한 차트를 생성 중...")
                chart_filename = draw_chart(stock_code, stock_name)
                print(f"Generated chart file: {chart_filename}")
                if os.path.exists(chart_filename):
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(chart_filename, 'rb'))
                else:
                    await update.message.reply_text(f"차트 파일을 찾을 수 없습니다: {chart_filename}")

                # /start 명령을 자동으로 호출
                await start(update, context)
            else:
                buttons = [[InlineKeyboardButton(f"{result['name']} ({result['code']})", callback_data=result['code'])] for result in results]
                reply_markup = InlineKeyboardMarkup(buttons)
                await update.message.reply_text("검색 결과를 선택하세요:", reply_markup=reply_markup)
                context.user_data['search_results'] = results
        else:
            await update.message.reply_text("검색 결과가 없습니다. 다시 시도하세요.")
        
        context.user_data['next_command'] = None

async def select_stock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    selected_code = query.data
    results = context.user_data.get('search_results', [])

    for result in results:
        if result['code'] == selected_code:
            stock_name, stock_code = result['name'], result['code']
            await query.edit_message_text(f"{stock_name} ({stock_code})에 대한 차트를 생성 중...")
            chart_filename = draw_chart(stock_code, stock_name)
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(chart_filename, 'rb'))
            break

    # /start 명령을 자동으로 호출
    # chat_id와 message_id를 사용하여 새로운 Update 객체 생성
    await start(update, context)

def main():
    secret_key = SecretKey()
    secret_key.load_secrets()
    
    token = secret_key.TELEGRAM_BOT_TOKEN_REPORT_ALARM_SECRET
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(select_stock, pattern=r'^\d{6}$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
