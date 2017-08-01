from Queue import Queue
from datetime import datetime
from threading import Thread


class TaskQueue(Thread, Queue):
    def __init__(self):
        Queue.__init__(self)
        Thread.__init__(self)
        self.establish_time = datetime.now()

    def run(self, next=False):
        pass
