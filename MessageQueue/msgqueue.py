# coding=utf-8
import os
import shutil
import time
from Queue import Queue
from threading import Thread

from MessageQueue import logger


class MessageQueue(Thread):
    def __init__(self, filename, timer=10):
        Thread.__init__(self)
        self.queue = Queue()
        self.filename = filename
        self.timer = timer
        self.establish_date = time.strftime("%Y-%m-%d")

    def run(self):
        while True:
            current_date = time.strftime("%Y-%m-%d")
            if current_date != self.establish_date:
                shutil.move("Flows/{0}.out".format(self.filename),
                            "Flows/{0}.{1}.out".format(self.filename, self.establish_date))
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

class LogQueue(MessageQueue):
    def sink(self):
        if not os.path.exists("Flows"):
            os.mkdir("Flows")
        with open("Flows/{0}.out".format(self.filename), "ab+") as f:
            while not self.queue.empty():
                f.write(self.queue.get() + "\n")
