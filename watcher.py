import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from dotenv import load_dotenv
import threading

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = subprocess.Popen([sys.executable, self.script])
        self.start_time = time.time()
        self.env = self.load_environment()
        self.timer = None
        self.start_timer()

    def load_environment(self):
        load_dotenv()  # .env 파일의 환경 변수를 로드합니다
        return os.getenv('ENV')

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            self.restart_script()

    def restart_script(self):
        print("Changes detected. Restarting script...")
        self.process.terminate()
        self.process = subprocess.Popen([sys.executable, self.script])
        self.start_time = time.time()  # 스크립트가 재시작되면 타이머도 초기화
        self.start_timer()

    def start_timer(self):
        if self.env != 'production':
            if self.timer:
                self.timer.cancel()  # 기존 타이머 취소
            self.timer = threading.Timer(10800, self.terminate_if_long_running)
            self.timer.start()

    def terminate_if_long_running(self):
        if time.time() - self.start_time >= 10800:  # 3시간이 초과되었는지 확인
            print("Script has been running for over 3 hours. Terminating...")
            self.process.terminate()

if __name__ == "__main__":
    script_to_watch = "main.py"  # 수정하고자 하는 봇 스크립트 이름
    event_handler = ChangeHandler(script=script_to_watch)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
