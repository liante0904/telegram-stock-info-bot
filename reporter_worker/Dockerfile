# 1. 빌드 스테이지
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Git 설치 (GitHub 의존성 패키지 설치를 위해 필수)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 캐시 효율을 위해 lock 파일과 pyproject.toml 먼저 복사
COPY pyproject.toml uv.lock ./

# 의존성 설치 (가상 환경 생성)
RUN uv sync --frozen --no-dev

# 2. 실행 스테이지 (더 가벼운 슬림 이미지)
FROM python:3.12-slim-bookworm

# 타임존 설정 (한국 시간 기준 스케줄링)
ENV TZ=Asia/Seoul
RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 빌더 스테이지에서 설치된 패키지 복사
COPY --from=builder /app/.venv /app/.venv

# 가상 환경을 사용하도록 PATH 설정
ENV PATH="/app/.venv/bin:$PATH"

# 소스 코드 복사 (필요한 부분만 쏙쏙!)
COPY modules/ ./modules/
COPY utils/ ./utils/
COPY models/ ./models/
COPY run/ ./run/
COPY make_kr_excel_quant.py .
COPY reporter_worker/scheduler.py .

# 파이썬 경로 및 출력 버퍼 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 실행
CMD ["python", "scheduler.py"]
