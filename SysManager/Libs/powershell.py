# -*- coding: UTF-8 -*-

import logging

from requests.exceptions import ConnectionError
from winrm.exceptions import InvalidCredentialsError

from ..excepts import WinRmNoValidConnectionsError, WinRmAuthenticationException


def run(client, module):
    ps_script = module.get('ps')
    args = module.get('args')
    if args and args.has_key('chdir'):
        base_dir = args['chdir']
    try:
        channel = client.run_ps(ps_script)
    except ConnectionError, err:
        logging.error(err)
        raise WinRmNoValidConnectionsError
    except InvalidCredentialsError, err:
        logging.error(err)
        raise WinRmAuthenticationException
    else:
        stdout, stderr = _stdout(), _stderr()
        stdout.channel.recv_exit_status = lambda: channel.status_code
        stdout.read = change_read_encoding(channel.std_out)
        stdout.readlines = change_readlines_encoding(stdout.read)
        stderr.read = change_read_encoding(channel.std_err)
        stderr.readlines = change_readlines_encoding(stderr.read)
        return stdout, stderr


class _output(object):
    def read(self):
        pass

    def readlines(self):
        pass


class _stdout(_output):
    def __init__(self):
        super(_stdout, self).__init__()
        self.channel = _channel()


class _channel():
    def recv_exit_status(self):
        pass


class _stderr(_output):
    pass


def change_read_encoding(cache):
    def _read():
        try:
            return cache.decode('utf-8').encode('utf-8').replace('\r\n', '\n')
        except UnicodeDecodeError:
            return cache.decode('gbk', 'ignore').encode('utf-8').replace('\r\n', '\n')

    return _read


def change_readlines_encoding(func):
    def _readlines():
        for line in func().split('\n'):
            if line != "":
                yield line

    return _readlines
