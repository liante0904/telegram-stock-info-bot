# Changelog

레거시 워크스페이스용 변경 이력 기록.

## 2026-04-28

- `secrets` 패키지명이 표준 라이브러리와 충돌하던 문제를 정리하고 `app_secrets`로 분리.
- 엔드포인트 상수를 레포 내부가 아니라 외부 `~/secrets/<workspace>/secrets.json` 에서 읽도록 변경.
- `docker-compose.yml` 에 `/home/ubuntu/secrets:/secrets:ro` 마운트와 `APP_SECRETS_*` 환경변수 추가.
- `telegram-bot` 컨테이너를 로컬 이미지 기준으로 다시 기동.
- `reporter-worker` 백필 발송 작업 재실행 및 `master` 빈커밋 배포 트리거 수행.

## 2026-04-18 ~ 2026-04-27

- `make_kr_excel_quant.py` 엑셀 스크리닝 발송 장애 원인 추적 및 복구.
- `2026-04-27` 스크리닝 파일 재생성 및 재발송.
- `2026-04-18` ~ `2026-04-24` 거래일 백필 순차 발송 작업 진행.

