# -*- coding: UTF-8 -*-


class InitialError(Exception):
    def __init__(self, param_name):
        Exception.__init__(self, 'Missing initial args [{}]'.format(param_name))


class DeserialError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
