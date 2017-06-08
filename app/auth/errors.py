# -*- coding: UTF-8 -*-

class AuthError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.status_code = 500

class AuthenticationError(AuthError):
    def __init__(self, msg='authentication error.'):
        super(AuthenticationError, self).__init__(msg)
        self.status_code = 401

class InvalidUsernameOrPassword(AuthError):
    def __init__(self, msg='Invalid username or password.'):
        super(InvalidUsernameOrPassword, self).__init__(msg)

class AuthorizationError(Exception):
    def __init__(self, msg='authorization error.'):
        super(AuthorizationError, self).__init__(msg)
        self.status_code = 403

class NoPrivilege(AuthorizationError):
    def __init__(self, msg='no privilege found.'):
        super(NoPrivilege, self).__init__(msg)

class LoopAuthorization(AuthorizationError):
    def __init__(self, msg='can not authorized by yourself.'):
        super(LoopAuthorization, self).__init__(msg)
