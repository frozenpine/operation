#from exceptions import ConfigInvalid

class SSHConfig:
    def __init__(self, ip, user, password=None, port=22, pKey=None, key_pass=None):
        if not password and not pKey:
            #raise ConfigInvalid('Either "password" or "pKey" must be specified.')
            raise Exception
        self.ssh_host = ip
        self.ssh_port = port
        self.ssh_user = user
        self.ssh_password = password
        self.ssh_key = pKey
        self.ssh_key_pass = key_pass
