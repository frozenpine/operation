# coding=utf-8
import json
import os
import shutil
import threading
import time
from Queue import Queue

from MessageQueue import logging


class BaseSinker(threading.Thread):
    def __init__(self, filename, timer=10):
        threading.Thread.__init__(self)
        self.queue = Queue()
        self.filename = filename
        self.timer = timer
        self.establish_date = time.strftime("%Y-%m-%d")
        if not os.path.exists("Flows"):
            os.mkdir("Flows")
            logging.warning('Directory(Flows) not exist, re-build.')
        if os.path.exists("Flows/{}.out".format(filename)):
            timestamp = time.localtime(os.stat("Flows/{}.out".format(filename)).st_ctime)
            create_date = "{}-{}-{}".format(timestamp[0], timestamp[1], timestamp[2])
            if time.strptime(self.establish_date, '%Y-%m-%d') != \
                time.strptime(create_date, '%Y-%m-%d'):
                shutil.move(
                    "Flows/{0}.out".format(filename),
                    "Flows/{0}_{1}.out".format(filename, create_date)
                )
                logging.info('New flow file({0}.out) created'.format(filename))

    def run(self):
        logging.info('Message sinker started.')
        while True:
            current_date = time.strftime("%Y-%m-%d")
            if current_date != self.establish_date:
                shutil.move("Flows/{0}.out".format(self.filename),
                            "Flows/{0}_{1}.out".format(self.filename, self.establish_date))
                self.establish_date = current_date
            self.sink()
            time.sleep(self.timer)

    def sink(self):
        pass

    def qsize(self):
        return self.queue.qsize()

    def empty(self):
        return self.queue.empty()

    def full(self):
        return self.queue.full()

    def put(self, item, block=True, timeout=None):
        self.queue.put(item, block, timeout)

    def put_nowait(self, item):
        return self.queue.put(item, False)

    def get(self, block=True, timeout=None):
        return self.queue.get(block, timeout)

    def get_nowait(self):
        return self.queue.get(False)

class LogSinker(BaseSinker):
    def sink(self):
        with open("Flows/{0}.out".format(self.filename), "ab+") as f:
            while not self.queue.empty():
                f.write(self.queue.get() + "\n")

class JSONSinker(BaseSinker):
    def sink(self):
        with open("Flows/{0}.out".format(self.filename), "ab+") as f:
            while not self.queue.empty():
                f.write(json.dumps(self.queue.get()) + "\n")
