import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import signal

class TkinterAppReloader(FileSystemEventHandler):
    def __init__(self, script_name):
        self.script_name = script_name
        self.process = None
        self.start_app()

    def start_app(self):
        if self.process:
            print(">> Stopping old process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()

        print(">> Starting app...")
        self.process = subprocess.Popen(["python", self.script_name])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f">> Detected change in: {event.src_path}")
            self.start_app()

    def stop(self):
        if self.process:
            print(">> Exiting...")
            self.process.terminate()

def run_dev_watcher(script_name="main.py"):
    event_handler = TkinterAppReloader(script_name)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()

    try:
        print(f">> Watching for changes in {os.getcwd()} ...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.stop()
        print(">> Dev watcher stopped.")

    observer.join()

if __name__ == "__main__":
    run_dev_watcher("main.py")  # Tkinter uygulamanın ana dosyasını buraya yaz
