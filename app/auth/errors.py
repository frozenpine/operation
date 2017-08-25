# -*- coding: UTF-8 -*-

class AuthError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.status_code = 500


class AuthenticationError(AuthError):
    def __init__(self, msg=u'验证错误'):
        super(AuthenticationError, self).__init__(msg)
        self.status_code = 401


class InvalidUsernameOrPassword(AuthError):
    def __init__(self, msg=u'错误的用户名或密码'):
        super(InvalidUsernameOrPassword, self).__init__(msg)


class AuthorizationError(AuthError):
    def __init__(self, msg=u'授权错误'):
        super(AuthorizationError, self).__init__(msg)
        self.status_code = 403


class NoPrivilege(AuthorizationError):
    def __init__(self, msg=u'用户无此权限'):
        super(NoPrivilege, self).__init__(msg)


class LoopAuthorization(AuthorizationError):
    def __init__(self, msg=u'不能给自己授权'):
        super(LoopAuthorization, self).__init__(msg)
