# coding=utf-8

from multiprocessing import Pool

from multiprocessing import cpu_count


class WorkerPool(object):
    def __init__(self):
        self.running_process = 0
        self.process_count = cpu_count()
        self.worker_pool = None

    def vacant(self):
        if self.running_process == self.process_count:
            return False
        else:
            return True

    def add_running_process(self):
        self.running_process += 1

    def minus_running_process(self):
        self.running_process -= 1

    def start(self):
        self.worker_pool = Pool(processes=self.process_count)

    def run(self, func, args):
        self.worker_pool.apply_sync(func, args)


worker_pool = WorkerPool()
