import schedule
import time
import subprocess
import os
import sys

def run_task(command):
    print(f"[{time.ctime()}] 작업 시작: {command}")
    # PYTHONPATH를 /app으로 설정하여 modules/를 바로 임포트 가능하게 함
    env = os.environ.copy()
    env["PYTHONPATH"] = "/app"
    
    result = subprocess.run(command, shell=True, env=env)
    if result.returncode == 0:
        print(f"[{time.ctime()}] 작업 완료")
    else:
        print(f"[{time.ctime()}] 작업 실패 (에러 코드: {result.returncode})")

# 15:40: 비동기 데이터 수집
schedule.every().day.at("15:40").do(run_task, "python run/fetch_kr_stock_quant_async.py")

# 16:00: 엑셀 생성 및 텔레그램 전송
schedule.every().day.at("16:00").do(run_task, "python make_kr_excel_quant.py")

print("📅 [Reporter Worker] 스케줄러가 시작되었습니다.")
print("🕒 15:40 KST: 데이터 수집")
print("🕒 16:00 KST: 엑셀 생성 및 전송")

while True:
    schedule.run_pending()
    time.sleep(60)
