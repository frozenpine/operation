# -*- coding: UTF-8 -*-
import re

import arrow
from flask import request, current_app
from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.exc import NoSuchColumnError
from sqlalchemy.sql import text
from werkzeug.exceptions import BadRequest

from SysManager.configs import SSHConfig, WinRmConfig
from SysManager.executor import Executor
from app import db
from app.models import DataSource, DataSourceType, DataSourceModel, TradeSystem
from restful.errors import (DataNotJsonError,
                            DataTypeError,
                            DataUniqueError,
                            DataNotNullError,
                            DataNotFoundError,
                            DataEnumValueError,
                            ApiError)
from restful.protocol import RestProtocol


class DataSourceApi(Resource):
    def __init__(self):
        super(DataSourceApi, self).__init__()

    def get(self, **kwargs):
        data_source = DataSource.find(**kwargs)
        if data_source is not None:
            return RestProtocol(data_source)
        else:
            return {'message': 'System vendor not found'}, 404


class DataSourceListApi(Resource):
    def __init__(self):
        super(DataSourceListApi, self).__init__()
        self.not_null_list = ['name', 'sys_id', 'src_type', 'src_model']

    def get(self):
        data_sources = DataSource.query.all()
        ret_dict = dict()
        datasource_type = DataSourceType.__members__.keys()
        for each in datasource_type:
            ret_dict.update({each: []})
        for each in data_sources:
            ret_dict.get(each.src_type.name).append(each.to_json())
        return RestProtocol(ret_dict)

    def post(self):
        try:
            try:
                data = request.get_json(force=True)
                for param in self.not_null_list:
                    if param not in data:
                        raise DataNotNullError('Please input {}'.format(param))
                if DataSource.find(name=data.get('name')):
                    raise DataUniqueError
            except BadRequest:
                return RestProtocol(DataNotJsonError())
            else:
                datasource = DataSource()
                datasource.name = data.get('name')
                datasource.description = data.get('description')
                datasource.sys_id = data.get('sys_id')
                datasource.src_type = data.get('src_type')
                datasource.src_model = data.get('src_model')
                datasource.disabled = data.get('disabled')
                datasource.source = dict()
                # 如果是SQL配置
                if datasource.src_type == DataSourceType.SQL.value:
                    # SQL一定有formatter
                    datasource.source.update({"formatter": data['formatter']})
                    # 从SQLDRIVER中根据protocol找到对应的driver
                    driver = current_app.config.get('SQL_DRIVER').get(data.get('protocol'))
                    if not driver:
                        raise DataNotNullError('Please input protocol and driver')
                    # 拼接uri
                    try:
                        uri = '{protocol}+{driver}://{login_user}:{login_pwd}@{ip}:{port}/{database}?charset={charset}'. \
                            format(protocol=data['protocol'], driver=driver, login_user=data['login_user'],
                                   login_pwd=data['login_pwd'], ip=data['ip'], port=data['port'],
                                   database=data['database'], charset=data['charset'])
                    except KeyError, e:
                        raise DataNotNullError(e)
                    # 如果是Custom 需定制化SQL
                    if datasource.src_model == DataSourceModel.Custom.value:
                        try:
                            sql = data['sql']
                        except KeyError:
                            raise DataNotNullError('Please input {}'.format('sql'))
                    # 不是Custom的情况下 写死SQL
                    elif datasource.src_model == DataSourceModel.Session.value:
                        sql = 'SELECT a.brokerid, a.userid, a.usertype, a.sessionid, a.frontid, a.logintime, a.ipaddress,' \
                              ' a.macaddress, a.userproductinfo, a.interfaceproductinfo, COUNT(a.id) AS total ' \
                              'FROM (SELECT * FROM t_oper_usersession ORDER BY id DESC) a GROUP BY userid'
                    elif datasource.src_model == DataSourceModel.Seat.value:
                        sql = 'SELECT seat.seat_name, sync.tradingday, sync.frontaddr, sync.seatid ' \
                              'FROM t_seat seat, t_sync_seat sync, t_capital_account ' \
                              'WHERE seat.seat_id = t_capital_account.seat_id AND sync.seatid=t_capital_account.account_id ' \
                              'AND sync.isactive = TRUE'
                    else:
                        raise DataEnumValueError('Unknown src model')
                    datasource.source.update({'uri': uri, 'sql': sql})
                # 如果是FILE配置
                elif datasource.src_type == DataSourceType.FILE.value:
                    # 如果是Custom 需定制化key_word 可选添加msg_pattern
                    if datasource.src_model == DataSourceModel.Custom.value:
                        try:
                            datasource.source.update({'key_words': data['key_words']})
                        except KeyError:
                            raise DataNotNullError('Please input key_words')
                        datasource.source.update({'msg_pattern': data.get('msg_pattern', '')})
                    # 不是Custom的情况下 写死key_words和msg_pattern
                    elif datasource.src_model == DataSourceModel.Seat.value:
                        key_words = {'disconn': u'断开', 'login': u'登录成功', 'conn': u'连接成功', 'logfail': u'登录失败'}
                        datasource.source.update({'key_words': key_words})
                        datasource.source.update(
                            {'msg_pattern':
                                 '.+TradeDate=\\[(?P<trade_date>[^]]+)\\]\\s+TradeTime=\\[(?P<trade_time>[^]]+)\\]'}
                        )
                    else:
                        raise DataEnumValueError('Unknown src model')
                    # 通过sysid找到对应的tradesystem
                    trade_system = TradeSystem.find(**{'id': datasource.sys_id})
                    # 拼接uri
                    if trade_system:
                        uri = '{protocol}://{login_user}:{login_pwd}@{ip}:22/#{log_file}?{module}'.format(
                            protocol=data['protocol'], login_user=trade_system.login_user,
                            login_pwd=trade_system.login_pwd,
                            ip=trade_system.ip, log_file=data['log_file'], module=data.get('module', 'customLog'))
                    else:
                        raise DataNotFoundError('tradesystem not found')
                    datasource.source.update({'uri': uri})
            db.session.add(datasource)
            db.session.commit()
            return RestProtocol(datasource)
        except ApiError, e:
            return RestProtocol(e)


class DataSourceResultApi(Resource):
    def __init__(self):
        super(DataSourceResultApi, self).__init__()
        self.app_context = current_app.app_context()
        self.rtn = list()

    def check_log(self, uri, data):
        reg = re.compile(
            r'^(?P<method>[^:]+)://(?P<user>[^:]+):(?P<pass>[^@]+)@(?P<ip>[^:]+):(?P<port>\d+)$'
        )
        pars = reg.match(uri).groupdict()
        res = {'svr': pars['ip'], 'logs': []}
        if pars['method'] == 'ssh':
            conf = SSHConfig(
                ip=pars['ip'],
                user=pars['user'],
                password=pars['pass'],
                port=int(pars['port'])
            )
        else:
            conf = WinRmConfig(
                ip=pars['ip'],
                user=pars['user'],
                password=pars['pass'],
                port=int(pars['port'])
            )
        executor = Executor.Create(conf)
        with self.app_context:
            logfile, module = data.pop('log_define').split('?')
            mod = dict()
            mod['name'] = module
            mod[module] = logfile.rstrip('/')
            mod['key_words'] = data.pop('key_words')
            result = executor.run(mod)
            if data['msg_pattern']:
                def repl(match):
                    for sub_match in match.groups():
                        if sub_match:
                            return match.group(0).replace(
                                sub_match, '<code>{}</code>'.format(sub_match))
                    return '<code>{}</code>'.format(match.group(0))

                result.lines = map(lambda x: re.sub(data['msg_pattern'], repl, x), result.lines)
            data_res = {
                'name': data['name'],
                'results': result.lines,
                'log_file': logfile.rstrip('/'),
                'update_time': arrow.utcnow().to(current_app.config['TIME_ZONE']).format('HH:mm:ss')
            }
            data_res.update(data)
            res['logs'].append(data_res)
            self.rtn.append(res)
            return self.rtn

    def get_datatable(self, uri, dt):
        try:
            sys_db = create_engine(uri).connect()
        except Exception:
            self.rtn.append({
                'db_host': re.findall(r'[^@]+@([^:/]+).*', uri)[0],
                'db_name': re.findall(r'[^@]+@[^/]+/([^?]+).*', uri)[0],
                'dt': None
            })
        else:
            rtn = {
                'db_host': re.findall(r'[^@]+@([^:/]+).*', uri)[0],
                'db_name': re.findall(r'[^@]+@[^/]+/([^?]+).*', uri)[0],
                'data_tables': []
            }
            data_table = {
                'name': dt.name,
                'formatter': dt.source['formatter'],
                'rows': []
            }
            results = sys_db.execute(text(dt.source['sql'])).fetchall()
            for row in results:
                tmp = {}
                for idx in xrange(len(dt.source['formatter'])):
                    try:
                        tmp[dt.source['formatter'][idx]['key']] = unicode(row[idx])
                    except (NoSuchColumnError, IndexError):
                        tmp[dt.source['formatter'][idx]['key']] = \
                            dt.source['formatter'][idx]['default']
                data_table['rows'].append(tmp)
            with self.app_context:
                data_table['update_time'] = arrow.utcnow() \
                    .to(current_app.config['TIME_ZONE']).format('HH:mm:ss')
            rtn['data_tables'].append(data_table)
            self.rtn.append(rtn)
            return self.rtn

    def get(self, **kwargs):
        data_source = DataSource.find(**kwargs)
        src_type = data_source.src_type
        src_model = data_source.src_model
        source = data_source.source
        if src_model.value != DataSourceModel.Custom.value:
            raise DataTypeError('Please select a custom datasource')
        if src_type.value == DataSourceType.FILE.value:
            data = ({
                'name': data_source.name,
                'formatter': data_source.source.get('formatter'),
                'msg_pattern': data_source.source.get('msg_pattern'),
                'key_words': data_source.source['key_words'],
                'log_define': source.get('uri').split('#')[1]
            })
            data_res = self.check_log(source.get('uri').split('#')[0].rstrip('/'), data)
            return RestProtocol({'FILE': data_res, 'SQL': list()})
        if src_type.value == DataSourceType.SQL.value:
            data_res = self.get_datatable(source.get('uri'), data_source)
            return RestProtocol({'FILE': list(), 'SQL': data_res})
