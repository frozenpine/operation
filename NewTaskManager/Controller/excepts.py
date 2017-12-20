# -*- coding: UTF-8 -*-
""" Exception definetion for TaskManager's Controller
"""



class RPCError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class QueueError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
