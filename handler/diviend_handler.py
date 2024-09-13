from telegram import Update
from telegram.ext import CallbackContext
from module.naver_stock_quant import fetch_dividend_total_stock_count


async def send_dividend_total_stock_count(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    try:
        # 국내 배당 종목 수를 가져옴
        dividend_total_stock_count = fetch_dividend_total_stock_count()
        dividend_message = (
            f"*국내 배당 종목 수는 {dividend_total_stock_count}개입니다\\.*\n\n"
            "필요한 *종목 수*를 전송해주세요\\.\n\n"
            "*0* 혹은 *아무 키*나 보내면 *전체 종목*이 전송됩니다\\."
        )
        await context.bot.send_message(chat_id=chat_id, text=dividend_message, parse_mode='MarkdownV2')
        
        # 사용자의 응답을 기다림
        user_response = await context.bot.get_updates(chat_id=chat_id, timeout=30)
        if user_response:
            user_message = user_response[-1].message.text
            
            # 입력된 값이 숫자인지 확인
            if user_message.isdigit():
                requested_stock_count = int(user_message)
            else:
                requested_stock_count = 0  # 숫자가 아닌 경우 전체 종목 전송

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
            text=f"국내 배당 종목 수를 가져오는 중 오류가 발생했습니다: {e}",
            parse_mode='MarkdownV2'
        )
