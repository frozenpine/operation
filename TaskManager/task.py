# coding=utf-8


class Task(dict):
    def __init__(self, task_uuid):
        dict.__init__(self)
        self["task_uuid"] = task_uuid
