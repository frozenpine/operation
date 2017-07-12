# coding=utf-8

from gevent.queue import JoinableQueue


class WorkerQueue(object):
    def __init__(self, uuid):
        self.uuid = uuid
        self.tasks_info = dict()
        self.worker_todo_task_queue = JoinableQueue()

    def get_worker_todo_task_queue(self):
        """
        从worker_todo_task_queue中去除一个task
        :return:
        """
        if not self.worker_todo_task_queue.empty():
            return self.worker_todo_task_queue.get()
        else:
            return None

    def put_worker_todo_task_queue(self, task):
        """
        向worker_todo_task_queue中放入一个task
        :param task: task
        :return:
        """
        self.worker_todo_task_queue.put(task)
