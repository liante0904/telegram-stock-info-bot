import os, requests
from pathlib import Path
from dotenv import load_dotenv
from config import SEND_DIR
from app_secrets.endpoints import TELEGRAM_SEND_DOCUMENT_URL

def send_to_telegram(file_name, target_date):
    BASE_DIR = Path(__file__).parent.parent.resolve()
    load_dotenv(dotenv_path=BASE_DIR / ".env")
    FILE_PATH = SEND_DIR / file_name
    if not os.path.exists(FILE_PATH): return False
    token = os.getenv('TELEGRAM_BOT_TOKEN_PROD')
    chat_id = os.getenv('TELEGRAM_CHANNEL_ID_REPORT_ALARM')
    if not token or not chat_id: return False
    url = TELEGRAM_SEND_DOCUMENT_URL.format(token=token)
    caption = f"📊 [{target_date}] 주식 스크리닝 결과"
    with open(FILE_PATH, 'rb') as f:
        res = requests.post(url, data={'chat_id': chat_id, 'caption': caption}, files={'document': f})
    return res.status_code == 200
