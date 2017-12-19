# -*- coding: UTF-8 -*-
""" Exception definetion for TaskManager
"""


class InitialError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class DeserialError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
