# coding=utf-8

import psutil


class WorkerInfo(object):
    def __init__(self, vacant_info):
        cpu_info = psutil.cpu_percent()
        mem_info = psutil.virtual_memory().percent()
        vacant_info = vacant_info
