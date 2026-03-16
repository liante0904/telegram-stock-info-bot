# Oracle ARM Server Migration Guide (AMD to ARM)

이 문서는 기존 Oracle AMD 프리티어에서 신규 ARM 인스턴스로의 이전을 위한 가이드입니다.

## 1. 전제 조건 (Prerequisites)
- 새로운 Oracle ARM 인스턴스 SSH 접속 가능 여부 확인
- Git 설치 (`sudo apt update && sudo apt install git -y`)

## 2. uv 설치
Oracle ARM 환경(Ubuntu 등)에서 `uv`를 설치합니다.
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

## 3. 리포지토리 복제 및 환경 설정
```bash
git clone https://github.com/liante0904/telegram-stock-info-bot.git
cd telegram-stock-info-bot

# .env 파일 또는 API 키 설정 (기존 서버에서 복사)
# 예: nano .env
```

## 4. 가상환경 및 의존성 설치 (uv 활용)
`uv`는 ARM 아키텍처를 지원하며 매우 빠른 속도로 가상환경을 구성합니다.
```bash
uv sync
```

## 5. Systemd 서비스 등록
제공된 `deployment/telegram-bot.service` 파일을 시스템에 등록합니다.
(서비스 파일 내의 경로 `/home/ubuntu/dev/telegram-stock-info-bot`가 실제 설치 경로와 일치하는지 확인하십시오.)

```bash
# 서비스 파일을 시스템 디렉토리로 복사
sudo cp deployment/telegram-bot.service /etc/systemd/system/telegram-bot.service

# 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot.service
sudo systemctl start telegram-bot.service

# 상태 확인
sudo systemctl status telegram-bot.service
```

## 6. 로그 모니터링
서비스 로그를 확인하려면 다음 명령어를 사용하십시오.
```bash
journalctl -u telegram-bot.service -f
```
