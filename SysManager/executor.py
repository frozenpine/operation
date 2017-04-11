from os import path
from paramiko import SSHClient, AutoAddPolicy, RSAKey
#from exceptions import ModuleNotFound, SSHConnNotEstablished
from configs import SSHConfig

class Executor():
    def __init__(self, ssh_config):
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.load_system_host_keys()
        try:
            if ssh_config.ssh_key and path.isfile(ssh_config.ssh_key):
                self.pKeyConnect(ssh_config)
            else:
                self.passConnect(ssh_config)
        except Exception:
            raise

    def pKeyConnect(self, ssh_config):
        try:
            if ssh_config.ssh_key_pass:
                pKey = RSAKey.from_private_key_file(
                    filename=ssh_config.ssh_key,
                    password=ssh_config.ssh_key_pass
                )
            else:
                pKey = RSAKey.from_private_key_file(filename=ssh_config.ssh_key)
        except Exception:
            raise
        try:
            self.client.connect(
                hostname=ssh_config.ssh_host,
                port=ssh_config.ssh_port,
                username=ssh_config.ssh_user,
                pkey=pKey
            )
        except Exception:
            raise

    def passConnect(self, ssh_config):
        try:
            self.client.connect(
                hostname=ssh_config.ssh_host,
                port=ssh_config.ssh_port,
                username=ssh_config.ssh_user,
                password=ssh_config.ssh_password
            )
        except Exception:
            raise

    def run(self, module):
        '''
        if self.client:
            try:
                mod = importlib.import_module('{}'.format(module.get('name')), package='.Libs')
            except ImportError:
                #raise ModuleNotFound('Module with name({}) not found.'.format(module.get('name')))
                raise
            else:
                return mod.run(client=self.client, module=module)
        else:
            #raise SSHConnNotEstablished
            raise Exception
        '''
        #import Libs.shell as mod
        import_string = 'import Libs.{} as mod'.format(module.get('name'))
        exec import_string
        return mod.run(client=self.client, module=module)

if __name__ == '__main__':
    conf = SSHConfig('192.168.92.26', 'root', 'Quantdo@SH2016!')
    executor = Executor(conf)
    stdin, stdout, stderr = executor.run(
        {
            'name': 'df'
        }
    )
    return_code = stdout.channel.recv_exit_status()
    if return_code != 0:
        print stderr.read()
    else:
        print stdout.read()
