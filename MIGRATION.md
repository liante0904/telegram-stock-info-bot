# Oracle ARM Server Migration Guide (AMD to ARM)

이 문서는 오라클 프리티어 AMD 인스턴스에서 ARM 인스턴스로의 이전을 위한 가이드입니다.

## 1. 전제 조건 (Prerequisites)
- ARM 인스턴스에 SSH 접속 가능 확인
- Git 설치 (`sudo apt update && sudo apt install git -y`)

## 2. uv 설치 및 환경 구성
Oracle ARM(Ubuntu 등)에서 `uv`를 활용해 가상환경을 구성합니다.
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

## 3. 리포지토리 복제 및 환경 설정
```bash
git clone https://github.com/liante0904/telegram-stock-info-bot.git
cd telegram-stock-info-bot

# .env 파일 또는 API 키 수동 복사
# 예: nano .env
```

## 4. 가상환경 및 의존성 설치 (uv)
`uv`는 ARM에서도 매우 빠른 설치를 지원합니다.
```bash
uv sync
```

## 5. Systemd 서비스 등록
함께 저장된 `deployment/telegram-bot.service`를 사용하여 시스템에 등록합니다.
(서비스 파일 내 `WorkingDirectory`와 `ExecStart`의 절대 경로가 실제 설치 경로와 맞는지 확인하세요.)

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

## 6. 로그 확인
```bash
journalctl -u telegram-bot.service -f
```
