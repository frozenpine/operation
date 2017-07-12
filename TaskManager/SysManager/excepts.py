# -*- coding: UTF-8 -*-

class ExecuteError(Exception):
    def __init__(self, msg="Excute error."):
        Exception.__init__(self, msg)

class ConfigInvalid(Exception):
    def __init__(self, msg="Config Invalid."):
        Exception.__init__(self, msg)

class ModuleNotFound(ExecuteError):
    def __init__(self, name=''):
        super(ModuleNotFound, self).__init__("Module({}) not found.".format(name))

class SSHConnNotEstablished(ExecuteError):
    def __init__(self, msg="No SSH connection."):
        super(SSHConnNotEstablished, self).__init__(msg)

class ImportRSAkeyFaild(ExecuteError):
    def __init__(self, msg="Faild to import RSAKey for SSH connection."):
        super(ImportRSAkeyFaild, self).__init__(msg)