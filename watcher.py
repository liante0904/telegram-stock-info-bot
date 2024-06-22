import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = subprocess.Popen([sys.executable, self.script])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            self.restart_script()

    def restart_script(self):
        print("Changes detected. Restarting script...")
        self.process.terminate()
        self.process = subprocess.Popen([sys.executable, self.script])

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
