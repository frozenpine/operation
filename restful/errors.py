# -*- coding: UTF-8 -*-

class ApiError(Exception):
    def __init__(self, msg, error_code=1000):
        Exception.__init__(self, msg)
        self.error_code = error_code

class ExecuteTimeOutOfRange(ApiError):
    def __init__(self, time_range):
        super(ExecuteTimeOutOfRange, self).__init__(
            'execution time out of range[{range[0]} ~ {range[1]}].'.format(
                range=time_range
            )
        )
        self.error_code = 1001

class InvalidParams(ApiError):
    def __init__(self, msg='invalid execution params'):
        super(InvalidParams, self).__init__(msg)
        self.error_code = 1002

class ExecuteError(ApiError):
    def __init__(self, msg='execution failed.'):
        super(ExecuteError, self).__init__(msg)
        self.error_code = 1003

class ProxyExecuteError(ExecuteError):
    def __init__(self, msg='execution failed.'):
        super(ProxyExecuteError, self).__init__(msg)
        self.error_code = 1004

class DataError(Exception):
    def __init__(self):
        super(DataError, self).__init__()
        self.message = 'Basic data error'
        self.error_code = 1100

class DataNotJsonError(DataError):
    def __init__(self):
        super(DataNotJsonError, self).__init__()
        self.message = 'Invalid JSON'
        self.error_code = 1101

class DataNotNullError(DataError):
    def __init__(self):
        super(DataNotNullError, self).__init__()
        self.message = 'Required data can not be empty.'
        self.error_code = 1102

class DataUniqueError(DataError):
    def __init__(self):
        super(DataUniqueError, self).__init__()
        self.message = 'The same data exists in DB already.'
        self.error_code = 1103

class DataTypeError(DataError):
    def __init__(self):
        super(DataTypeError, self).__init__()
        self.message = 'Data type error occurs.'
        self.error_code = 1104

class DataEnumValueError(DataError):
    def __init__(self):
        super(DataEnumValueError, self).__init__()
        self.message = 'Data contains enum type, make sure its value is correct.'
        self.error_code = 1105
