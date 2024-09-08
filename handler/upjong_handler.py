from telegram import Update
from telegram.ext import CallbackContext
from module.naver_upjong_quant import fetch_upjong_list_API

# 업종 목록을 보여주는 함수 (인덱스 포함)
async def show_upjong_list(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    try:
        upjong_list = fetch_upjong_list_API()
        upjong_message = "업종 목록:\n"
        upjong_map = {i: (업종명, 등락률, 링크) for i, (업종명, 등락률, 링크) in enumerate(upjong_list, 1)}
        
        for i, (업종명, 등락률, _) in upjong_map.items():
            # 이스케이프 처리
            업종명 = 업종명.replace('.', '\\.')
            등락률 = 등락률.replace('.', '\\.').replace('-', '\\-').replace('+', '\\+')
            upjong_message += f"{i}\\. *{업종명}*   \\[{등락률}\\]\n"
            # print(upjong_message)

        upjong_message += "\n업종 번호 혹은 업종명\\(정확하게\\) 입력하세요\\."
        context.user_data['upjong_map'] = upjong_map  # 업종 맵을 저장하여 나중에 사용할 수 있게 함
        await context.bot.send_message(chat_id=chat_id, text=upjong_message, parse_mode='MarkdownV2')
        context.user_data['next_command'] = 'naver_upjong_quant'
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"업종 목록을 가져오는 중 오류가 발생했습니다: {e}")
