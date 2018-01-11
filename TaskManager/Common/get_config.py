# coding=utf-8

import os
import os.path
from ConfigParser import ConfigParser


class Default(object):
    default = {
        'FLASK':
            {
                'LISTENING': '127.0.0.1',
                'PORT': 5000,
            },
        'CONTROLLER':
            {'RPCSERVER': '127.0.0.1',
             'RPCPORT': 6000,
             'LISTENING': '127.0.0.1',
             'PORT': 7000,
             'PEER': 1
             },
        'WORKER':
            {
                'MASTER': ('127.0.0.1', 7000),
                'SLAVE': (),
            }
    }

    @classmethod
    def get(cls, section, param):
        if section in cls.default and param in cls.default.get(section):
            return cls.default.get(section).get(param)
        else:
            return None


class Config(object):
    config_file = (os.path.join(os.path.dirname(__file__), 'config.ini'))
    cf = ConfigParser()
    cf.read('config.ini')

    @classmethod
    def get_param(cls, section, param):
        env_param = os.environ.get(param)
        file_param = cls.cf.get(section, param)
        default_param = Default.get(section, param)
        if env_param:
            return env_param
        elif file_param:
            return file_param
        elif default_param:
            return default_param
        else:
            return None
