from telegram import Update
from telegram.ext import CallbackContext
from module.naver_stock_quant import fetch_dividend_stock_list_API



async def send_dividend_stock_excel_quant(update: Update, context: CallbackContext) -> None:
    try:
        user_id = str(update.effective_user.id)
        user_input = update.message.text
        chat_id = update.effective_chat.id
        next_command = context.user_data.get('next_command')
        
        # API 호출하여 전체 배당 종목 수 가져오기
        dividend_data = fetch_dividend_stock_list_API(page=1, pageSize=1)  # pageSize=1로 최소 데이터 호출
        dividend_total_stock_count = dividend_data.get('totalCount', 0)

        # 사용자의 응답을 기다림
        user_message = user_input.strip()

        # 입력된 값이 숫자인지 확인
        if user_message.isdigit():
            requested_stock_count = int(user_message)
        else:
            requested_stock_count = 0  # 숫자가 아닌 경우 전체 종목 전송

        # 입력된 종목 수가 전체 배당 종목 수 범위 내인지 확인
        if 1 <= requested_stock_count <= dividend_total_stock_count:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"*{requested_stock_count}*개의 종목을 전송합니다\\.",
                parse_mode='MarkdownV2'
            )
            # 요청된 수 만큼 종목 전송 로직 추가 (필요 시 함수 호출)
        else:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"*전체 종목*을 전송합니다\\.",
                parse_mode='MarkdownV2'
            )
            # 전체 종목 전송 로직 추가 (필요 시 함수 호출)
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"오류가 발생했습니다: {e}",
            parse_mode='MarkdownV2'
        )
