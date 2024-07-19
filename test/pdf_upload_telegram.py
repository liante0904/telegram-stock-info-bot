import os
from dotenv import load_dotenv
import telegram
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
import asyncio

# .env 파일의 환경 변수를 로드합니다
load_dotenv()

# 환경 변수에 따라 토큰 선택
env = os.getenv('ENV')
print(env)
if env == 'production':
    token = os.getenv('TELEGRAM_BOT_TOKEN_PROD')
else:
    token = os.getenv('TELEGRAM_BOT_TOKEN_TEST')

# 업로드된 파일의 URL을 반환하는 비동기 함수
async def get_file_url(file_id):
    bot = telegram.Bot(token=token)
    file = await bot.get_file(file_id)
    return file.file_path

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('PDF 파일을 업로드하세요.')

async def handle_file(update: Update, context: CallbackContext) -> None:
    file = update.message.document
    if file.mime_type == 'application/pdf':
        file_id = file.file_id
        file_url = await get_file_url(file_id)
        await update.message.reply_text(f'파일이 업로드되었습니다: {file_url}')
    else:
        await update.message.reply_text('PDF 파일만 업로드 가능합니다.')

async def set_commands(bot):
    commands = [
        BotCommand("start", "PDF 업로드 테스트")
    ]
    await bot.set_my_commands(commands)

def main():
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))  # /start 명령어 추가
    application.add_handler(MessageHandler(filters.Document.PDF, handle_file))

    # asyncio 이벤트 루프에서 명령어 설정
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_commands(application.bot))

    application.run_polling()

if __name__ == '__main__':
    main()
