from pathlib import Path
from app_secrets.endpoints import (
    NAVER_KOSPI_MARKET_URL, NAVER_KOSDAQ_MARKET_URL,
    NAVER_STOCK_PAGE_URL, TELEGRAM_SEND_DOCUMENT_URL,
)

BASE_DIR = Path(__file__).parent.parent.resolve()
SEND_DIR = BASE_DIR / "send"
CACHE_DB_PATH = BASE_DIR / "cache" / "stock_cache.db"
MAX_WORKERS = 4
HEADERS = {"User-Agent": "Mozilla/5.0"}
