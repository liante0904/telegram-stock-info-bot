import json
import os
from pathlib import Path


DEFAULT_WORKSPACE = "telegram-stock-info-bot"
SECRETS_ROOT = Path(os.getenv("APP_SECRETS_ROOT", "/secrets"))
SECRETS_WORKSPACE = os.getenv("APP_SECRETS_WORKSPACE", DEFAULT_WORKSPACE)
SECRETS_FILE = os.getenv("APP_SECRETS_FILE", "secrets.json")


def _resolve_secrets_path() -> Path:
    return SECRETS_ROOT / SECRETS_WORKSPACE / SECRETS_FILE


def _load_endpoints() -> dict:
    path = _resolve_secrets_path()
    if not path.exists():
        raise FileNotFoundError(
            f"External endpoints file not found: {path}. "
            "Set APP_SECRETS_ROOT / APP_SECRETS_WORKSPACE, or mount the secrets directory."
        )

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid endpoints file format: {path} must contain a JSON object")

    return data


_ENDPOINTS = _load_endpoints()


def _get(name: str) -> str:
    value = _ENDPOINTS.get(name)
    if not isinstance(value, str) or not value:
        raise KeyError(
            f"Missing required endpoint key '{name}' in {_resolve_secrets_path()}"
        )
    return value


# Naver Mobile Stock API
NAVER_INDUSTRY_URL = _get("NAVER_INDUSTRY_URL")
NAVER_INDUSTRY_PAGED_URL = _get("NAVER_INDUSTRY_PAGED_URL")
NAVER_KOSPI_INDEX_URL = _get("NAVER_KOSPI_INDEX_URL")
NAVER_KOSPI_MARKET_URL = _get("NAVER_KOSPI_MARKET_URL")
NAVER_KOSDAQ_MARKET_URL = _get("NAVER_KOSDAQ_MARKET_URL")
NAVER_AC_URL = _get("NAVER_AC_URL")
NAVER_FINANCE_BASE = _get("NAVER_FINANCE_BASE")
NAVER_COMPANY_REPORT_URL = _get("NAVER_COMPANY_REPORT_URL")
NAVER_FINANCE_STOCK_PREFIX = _get("NAVER_FINANCE_STOCK_PREFIX")

# Naver API (api.stock.naver.com)
NAVER_NYSE_MARKET_URL = _get("NAVER_NYSE_MARKET_URL")
NAVER_NASDAQ_MARKET_URL = _get("NAVER_NASDAQ_MARKET_URL")
NAVER_AMEX_MARKET_URL = _get("NAVER_AMEX_MARKET_URL")

# URL templates
NAVER_DIVIDEND_RATE_URL = _get("NAVER_DIVIDEND_RATE_URL")
NAVER_STOCK_BASIC_URL = _get("NAVER_STOCK_BASIC_URL")
NAVER_STOCK_INTEGRATION_URL = _get("NAVER_STOCK_INTEGRATION_URL")
NAVER_STOCK_FINANCE_URL = _get("NAVER_STOCK_FINANCE_URL")
NAVER_STOCK_PAGE_URL = _get("NAVER_STOCK_PAGE_URL")
NAVER_DOMESTIC_STOCK_URL = _get("NAVER_DOMESTIC_STOCK_URL")
NAVER_REUTERS_BASIC_URL = _get("NAVER_REUTERS_BASIC_URL")
NAVER_NATION_INDEX_URL = _get("NAVER_NATION_INDEX_URL")
NAVER_STOCK_CHART_URL = _get("NAVER_STOCK_CHART_URL")

# Telegram API
TELEGRAM_SEND_DOCUMENT_URL = _get("TELEGRAM_SEND_DOCUMENT_URL")
