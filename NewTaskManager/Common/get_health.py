# coding=utf-8

import psutil


def get_cpu():
    return psutil.cpu_percent()


def get_mem():
    return psutil.virtual_memory().percent
