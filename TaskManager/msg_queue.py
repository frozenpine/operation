# coding=utf-8

from gevent.queue import JoinableQueue


class MsgQueue(object):
    def __init__(self):
        self.todo_task_queue = JoinableQueue()


msg_queue = MsgQueue()
