# coding=utf-8

from enum import Enum


class EventName(Enum):
    TaskDispath = 10
    TaskResult = 11


class MessageEvent(object):
    def __init__(self, event_name, event_data):
        self._name = event_name
        self._data = event_data

    @property
    def Name(self):
        return self._name

    @property
    def Data(self):
        return self._data
