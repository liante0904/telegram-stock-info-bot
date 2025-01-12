from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from datetime import datetime, timedelta
import os
import sys
import json
from dotenv import load_dotenv
from datetime import datetime
# 현재 스크립트의 상위 디렉터리를 모듈 경로에 추가(package 폴더에 있으므로)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.naver_stock_report import search_stock_report_pc
from utils.naver_stock_util import search_stock_code
from utils.recent_search_util import save_recent_searches
from db.report_dao import ReportDAO

async def process_request_report(update: Update, context: CallbackContext, chat_id: str, message=None) -> None:
    """
    Handle user search requests for reports and send results with pagination.
    """
    user_input = message.text if message else context.user_data.get('last_keyword')
    db = ReportDAO()
    
    # Pagination
    limit = 20
    offset = context.user_data.get('offset', 0)
    
    # Fetch search results count
    resultsCount = db.SelSearchReportsCount(user_input)
    
    # Fetch search results
    results = db.SelSearchReports(user_input, limit=limit, offset=offset)
    
    if not results:
        # Check if we're at the last page
        if offset > 0:
            await context.bot.send_message(chat_id=chat_id, text="더 이상 조회할 데이터가 없습니다.")
        else:
            await context.bot.send_message(chat_id=chat_id, text="검색 결과가 없습니다.")
        return

    # Create the search summary message
    search_summary = f"사용자의 검색어 [{user_input}]는 총 *{resultsCount}*건 중 {offset+1} ~ {offset+len(results)}건 표시:\n\n"

    # Update the message format to match the requested template
    send_text = search_summary  # Add search summary at the top
    for idx, result in enumerate(results, start=1 + offset):
        link = result.get('TELEGRAM_URL') or result.get('DOWNLOAD_URL') or result.get('ATTACH_URL', '링크 없음')

        # LS증권의 경우 링크 두 개 표시
        if result['FIRM_NM'] == 'LS증권':
            key_link = result['KEY']
            send_text += (
                f"*{result['ARTICLE_TITLE'].strip()}*\n"
                f"{result['FIRM_NM'].strip()} / {result['REG_DT'].strip()} / "
                f"[링크]({link}) | [게시글링크]({key_link})\n\n"
            )
        else:
            # 일반적인 경우
            send_text += (
                f"*{result['ARTICLE_TITLE'].strip()}*\n"
                f"{result['FIRM_NM'].strip()} / {result['REG_DT'].strip()} / "
                f"[링크]({link})\n\n"
            )

    # Append the search summary at the bottom
    send_text += search_summary

    # Generate pagination buttons
    buttons = [
        # 한 줄에 두 개의 버튼: 메인 메뉴 이동과 다른 키워드 검색
        [
            InlineKeyboardButton("메인 메뉴 이동", callback_data="main_menu"), 
            InlineKeyboardButton("다른 키워드 검색", callback_data="search_new_keyword")
        ],
    ]
    if offset > 0:
        buttons.append([InlineKeyboardButton("⬅️ 이전 20건", callback_data=f"search:{user_input}:{offset-limit}")])
    if len(results) == limit:
        buttons.append([InlineKeyboardButton("➡️ 다음 20건", callback_data=f"search:{user_input}:{offset+limit}")])

    reply_markup = InlineKeyboardMarkup(buttons)

    # Send the formatted message with pagination buttons
    await context.bot.send_message(
        chat_id=chat_id, 
        text=send_text, 
        parse_mode='Markdown', 
        disable_web_page_preview=True, 
        reply_markup=reply_markup
    )
    context.user_data['last_keyword'] = user_input
    context.user_data['offset'] = offset

async def fetch_and_send_reports(update: Update, context: CallbackContext, user_id: str, message, stock_name: str, stock_code: str, writeFromDate: str, writeToDate: str) -> None:
    await message.reply_text(f"{stock_name}({stock_code}) 키워드 레포트를 검색 중...")

    # 최근 검색 종목에 추가 (중복 방지)
    if user_id not in context.bot_data['recent_searches']:
        context.bot_data['recent_searches'][user_id] = []
    if not any(search['name'] == stock_name for search in context.bot_data['recent_searches'][user_id]):
        context.bot_data['recent_searches'][user_id].append({'name': stock_name, 'code': stock_code})
    save_recent_searches(context.bot_data['recent_searches'])

    report_results = search_stock_report_pc(stock_name, stock_code, writeFromDate, writeToDate)
    if report_results:
        # 발간일을 기준으로 오름차순 정렬
        report_results.sort(key=lambda x: x['date'])

        report_messages = [
            f"제목 : *{result['title']}*\n"
            f"증권사: {result['broker']}\n"
            f"발간일: {result['date']}\n"
            f"[링크]({result['link']})"
            for result in report_results
        ]

        # 메시지 나누어서 전송
        header = f"*종목명*: {stock_name} ({stock_code})\n\n"
        for i in range(0, len(report_messages), 5):
            await message.reply_text(header + "\n\n".join(report_messages[i:i+5]), parse_mode='Markdown', disable_web_page_preview=True)
            header = ""

        await message.reply_text(f"{stock_name}({stock_code})에 대한 레포트를 찾을 수 없습니다.")
        # buttons = [[InlineKeyboardButton("이전 검색", callback_data='previous_search')]]
        # reply_markup = InlineKeyboardMarkup(buttons)
        # await message.reply_text("이전일자(2주일) 혹은 다른 종목을 검색할 수 있습니다.", reply_markup=reply_markup)
    else:
        await message.reply_text(f"{stock_name}({stock_code})에 대한 레포트를 찾을 수 없습니다.")

