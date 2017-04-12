# -*- coding: UTF-8 -*-

class ConfigInvalid(Exception):
    def __init__(self, msg="Config Invalid."):
        self.message = msg
        Exception.__init__(self, msg)

class ModuleNotFound(Exception):
    def __init__(self, msg="Module not found."):
        self.message = msg
        Exception.__init__(self, msg)

class SSHConnNotEstablished(Exception):
    def __init__(self, msg="No SSH connection."):
        self.message = msg
        Exception.__init__(self, msg)

class ImportRSAkeyFaild(Exception):
    def __init__(self, msg="Faild to import RSAKey for SSH connection."):
        self.message = msg
        Exception.__init__(self, msg)
