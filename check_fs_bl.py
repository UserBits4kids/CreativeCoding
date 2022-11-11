import sys
import os
import datetime
import time
import logging
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import filecmp

USB_PATH = "/mnt/usb"
WIFI_PATH = os.getcwd()+"/wifi"
BLUETOOTH_PATH = os.getcwd()+"/bluetooth"
DATA_LOCATION = "/piusb.bin"
MOUNT = "sudo mount "+DATA_LOCATION+" "+USB_PATH
UNMOUNT = "sudo umount "+USB_PATH
ENABLE_OTG = "sudo modprobe g_mass_storage file="+DATA_LOCATION+" stall=0 removable=1" 
DISABLE_OTG = "sudo modprobe -r g_mass_storage"

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%s")
    path = sys.argv[1] if len(sys.argv) > 1 else BLUETOOTH_PATH
    print("PATH:" + path)
    event_handler = Handler(path)
    #event_handler.replug()
    print("Starting Watching")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        event_handler.stop()
    event_handler.join()
    print("Stopped Watching")

class Handler(FileSystemEventHandler):
    def __init__(self, path):
        self.path = path
        self.observer = Observer()
        self.observer.schedule(self, path=path, recursive=True)
        self.observer.start()
        self.terminating = threading.Lock()
        self.timeout_start = None
        self.timeout_lock = threading.Lock()

    def stop(self):
        self.observer.stop()

    def join(self):
        self.observer.join()

    def terminate(self):
        self.terminating.acquire()
        print("Stopped Watching")
        os.execl(sys.executable, sys.executable, *sys.argv)
        #for Windows
        self.terminating.release()
        exit(0)

    def move(self):
        os.system("for f in "+BLUETOOTH_PATH+"/*.dst; do mv $f ${f%.dst}_$(date +'%Y-%m-%d-%H-%M-%s').dst; done ")
        os.system("mv "+BLUETOOTH_PATH+"/* "+ WIFI_PATH)
        pass

    def on_any_event(self, event):
        if event.event_type == 'closed' or event.event_type == 'moved' or event.event_type == 'deleted':
        # Event is modified, you can process it now
            print("Watchdog received modified event - % s." % event.src_path)
            self.observer.stop()
            self.move()
            self.terminate()
        print(event.event_type)

if __name__ == '__main__':
    main()

