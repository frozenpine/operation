# -*- coding: UTF-8 -*-
from flask_restful import Resource
from app import db
from app.models import ConfigFile, ConfigType, TradeSystem
from flask import request, current_app
from werkzeug.exceptions import BadRequest
from restful.errors import (DataNotJsonError,
                            DataNotNullError,
                            DataEnumValueError,
                            ApiError)
from restful.protocol import RestProtocol
from SysManager.configs import SSHConfig
from SysManager.executor import Executor
import arrow
import os


class ConfigFileListApi(Resource):
    def __init__(self):
        super(ConfigFileListApi, self).__init__()
        self.not_null_list = ['name', 'dir', 'file', 'config_type', 'sys_id']
        self.system_list = []

    def gather_systems(self, parent_sys):
        self.system_list.append(parent_sys)
        for child_sys in parent_sys.child_systems:
            if child_sys.disabled is False:
                self.gather_systems(child_sys)

    def get(self, **kwargs):
        system = TradeSystem.find(**kwargs)
        if system:
            self.gather_systems(system)
            ''' for sys in self.system_list:
                # config_files = ConfigFile.query.filter_by(sys_id=sys.id).all()
                self.config_file_list.extend(sys.config_files) '''
            conf_file_list = ConfigFile.query.filter(
                ConfigFile.sys_id.in_([sys.id for sys in self.system_list])
            ).all()
            return RestProtocol(conf_file_list)

        else:
            return RestProtocol(message='System not found', error_code=-1), 404

    def post(self):
        try:
            data = request.get_json(force=True)
            for param in self.not_null_list:
                if not data.get(param):
                    raise DataNotNullError('Please input {}'.format(param))
            ConfigType[data.get('config_type')]
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        except ApiError as e:
            return RestProtocol(e)
        except KeyError:
            return RestProtocol(DataEnumValueError())
        else:
            config_file = ConfigFile()
            config_file.name = data.get('name')
            config_file.sys_id = data.get('sys_id')
            config_file.config_type = ConfigType[data.get('config_type')]
            config_file.dir = data.get('dir')
            config_file.file = data.get('file')
            system = TradeSystem.find(id=data.get('sys_id'))
            if system:
                mod = {
                    'name': 'md5',
                    'args': {
                        'dir': data.get('dir'),
                        'file': data.get('file')
                    }
                }
                conf = SSHConfig(system.ip,
                                 system.user,
                                 system.password)
                executor = Executor.Create(conf)
                result = executor.run(mod)
                if result.return_code == 0:
                    config_file.hash_code = result.lines[0]
                    config_file.timestamp = arrow.utcnow()

                # Make directory for config file
                if not os.path.exists(current_app.config['CONFIG_FILES']):
                    os.mkdir(current_app.config['CONFIG_FILES'])
                os.chdir(os.path.join(current_app.config['CONFIG_FILES']))
                dir_name = system.name + '_' + system.ip
                if not os.path.exists(dir_name):
                    os.mkdir(dir_name)
                config_file.storage = current_app.config['CONFIG_FILES'] + '/' + os.path.join(dir_name)
                os.chdir('../')
            db.session.add(config_file)
            db.session.commit()
            return RestProtocol(config_file)


class ConfigFileApi(Resource):
    def __init__(self):
        super(ConfigFileApi, self).__init__()

    def get(self, **kwargs):
        config_file = ConfigFile.find(**kwargs)
        if config_file:
            return RestProtocol(config_file)
        else:
            return RestProtocol(message='Config file not found', error_code=-1), 404

    def put(self):
        pass


class ConfigFileCheckApi(Resource):
    def __init__(self):
        super(ConfigFileCheckApi, self).__init__()
        self.system_list = []
        self.config_file_list = []
        self.executor_dict = {}
        self.check_result = {}

    def gather_systems(self, parent_sys):
        self.system_list.append(parent_sys)
        for child_sys in parent_sys.child_systems:
            if child_sys.disabled is False:
                self.gather_systems(child_sys)

    def get(self, **kwargs):
        system = TradeSystem.find(**kwargs)
        if system:
            self.gather_systems(system)
            for sys in self.system_list:
                self.config_file_list.extend(sys.config_files)
                conf = SSHConfig(sys.ip,
                                 sys.user,
                                 sys.password)
                executor = Executor.Create(conf)
                self.executor_dict[sys.id] = executor
            for config_file in self.config_file_list:
                mod = {
                    'name': 'md5',
                    'args': {
                        'dir': config_file.dir,
                        'file': config_file.file
                    }
                }
                conf_sys = TradeSystem.find(id=config_file.sys_id)
                if conf_sys:
                    result = self.executor_dict[conf_sys.id].run(mod)
                    if result.return_code == 0:
                        # 'True' means not change, 'False' means change
                        if result.lines[0] == config_file.hash_code:
                            self.check_result[config_file.name] = True, config_file.dir
                        if result.lines[0] != config_file.hash_code:
                            self.check_result[config_file.name] = False, config_file.dir
            return RestProtocol(self.check_result)
        else:
            return RestProtocol(message='System not found', error_code=-1), 404
