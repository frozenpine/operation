from Queue import Queue
from threading import Thread
from datetime import datetime

class TaskQueue(Thread, Queue):
    def __init__(self):
        Queue.__init__(self)
        Thread.__init__(self)
        self.establish_time = datetime.now()

    def run(self, next=False):
        pass
