# -*- coding: UTF-8 -*-

class ApiError(Exception):
    def __init__(self, msg, status_code=500):
        Exception.__init__(self, msg)
        self.status_code = status_code

class ExecuteTimeOutOfRange(ApiError):
    def __init__(self, time_range):
        super(ExecuteTimeOutOfRange, self).__init__(
            'execution time out of range[{range[0]} ~ {range[1]}].'.format(
                range=time_range
            )
        )
        self.status_code = 403

class InvalidParams(ApiError):
    def __init__(self, msg='invalid execution params'):
        super(InvalidParams, self).__init__(msg)
        self.status_code = 400

class ExecuteError(ApiError):
    def __init__(self, msg='execution failed.'):
        super(ExecuteError, self).__init__(msg)

class ProxyExecuteError(ExecuteError):
    def __init__(self, msg='execution failed.'):
        super(ProxyExecuteError, self).__init__(msg)
        self.status_code = 502
