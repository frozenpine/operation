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
    def __init__(self):
        super(ExecuteError, self).__init__()
        self.error_code = 1003
        self._msg = 'execution failed.'


class ProxyExecuteError(ExecuteError):
    def __init__(self, msg='execution failed.'):
        super(ProxyExecuteError, self).__init__(msg)
        self.error_code = 1004


class RestfulError(ApiError):
    def __init__(self, msg='Error occurs in restful framework.'):
        super(RestfulError, self).__init__(msg)
        self.error_code = 1005


class LoaderNotFoundError(ApiError):
    def __init__(self, msg='The corresponding loader does\'t exist. Maybe you upload the wrong file.'):
        super(LoaderNotFoundError, self).__init__(msg)
        self.error_code = 1006


class PlatFormNotFoundError(ApiError):
    def __init__(self, msg='We don\'t know what platform it is. Please input remote name'):
        super(PlatFormNotFoundError, self).__init__(msg)
        self.error_code = 1007


class DataNotJsonError(ApiError):
    def __init__(self, message='Invalid JSON'):
        super(DataNotJsonError, self).__init__(message)
        self.error_code = 1101
        self.data = None


class DataNotNullError(ApiError):
    def __init__(self, message='Required data can not be empty.'):
        super(DataNotNullError, self).__init__(message)
        self.error_code = 1102


class DataUniqueError(ApiError):
    def __init__(self, message='The same data exists in DB already.'):
        super(DataUniqueError, self).__init__(message)
        self.error_code = 1103


class DataTypeError(ApiError):
    def __init__(self, message='Data type error occurs.'):
        super(DataTypeError, self).__init__(message)
        self.error_code = 1104


class DataEnumValueError(ApiError):
    def __init__(self, message='Data contains enum type, make sure its value is correct.'):
        super(DataEnumValueError, self).__init__(message)
        self.error_code = 1105


class DataNotMatchError(ApiError):
    def __init__(self, message='Data must match'):
        super(DataNotMatchError, self).__init__(message)
        self.error_code = 1106


class DataNotFoundError(ApiError):
    def __init__(self, message='Data not found'):
        super(DataNotFoundError, self).__init__(message)
        self.error_code = 1107
