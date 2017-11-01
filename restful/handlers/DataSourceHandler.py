# -*- coding: UTF-8 -*-
from flask import request, current_app
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from app import db
from app.models import DataSource, DataSourceType, DataSourceModel, TradeSystem
from restful.errors import (DataNotJsonError,
                            DataUniqueError,
                            DataNotNullError,
                            DataNotFoundError,
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

    def put(self, **kwargs):
        datasource = DataSource.find(**kwargs)
        if datasource:
            try:
                data = request.get_json(force=True)
                if data.get('name'):
                    if datasource.name != data.get('name') and DataSource.find(name=data.get('name')):
                        raise DataUniqueError
            except BadRequest:
                return RestProtocol(DataNotJsonError())
            except DataUniqueError as e:
                return RestProtocol(e)
            else:
                datasource.name = data.get('name')
                datasource.description = data.get('description')
                datasource.sys_id = data.get('sys_id')
                datasource.src_type = data.get('src_type')
                datasource.src_model = data.get('src_model')
                datasource.source = data.get('source')
                datasource.disabled = data.get('disabled')
                db.session.add(datasource)
                db.session.commit()
                return RestProtocol(datasource)
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
            data = request.get_json(force=True)
            for param in self.not_null_list:
                if not data.get(param):
                    raise DataNotNullError('Please input {}'.format(param))
            if DataSource.find(name=data.get('name')):
                raise DataUniqueError
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        except ApiError as e:
            return RestProtocol(e)
        else:
            datasource = DataSource()
            datasource.name = data.get('name')
            datasource.description = data.get('description')
            datasource.sys_id = data.get('sys_id')
            datasource.src_type = data.get('src_type')
            datasource.src_model = data.get('src_model')
            datasource.source = data.get('source')
            datasource.disabled = data.get('disabled')
            # 获取connector中的配置
            connector = data.get('connector')
            # 如果是SQL配置
            if datasource.src_type == DataSourceType.SQL.value:
                # 从SQLDRIVER中根据protocol找到对应的driver
                connector.update({'driver': current_app.config['SQL_DRIVER'][connector['protocol']]})
                # 去除字典中无用的key
                if 'logfile' in connector:
                    connector.pop('logfile')
                if 'module' in connector:
                    connector.pop('module')
                # 拼接uri
                try:
                    uri = '{protocol}+{driver}://{login_user}:{login_pwd}@{ip}:{port}/#{database}?charset={charset}'. \
                        format(**connector)
                except KeyError, e:
                    raise DataNotNullError(e)
                # 如果是Custom 需定制化SQL
                if datasource.src_model == DataSourceModel.Custom.value:
                    try:
                        sql = data['sql']
                    except KeyError:
                        raise DataNotNullError('Please input {}'.format('sql'))
                # 不是Custom的情况下，写死SQL
                elif datasource.src_model == DataSourceModel.Session.value:
                    sql = 'SELECT a.brokerid, a.userid, a.usertype, a.sessionid, a.frontid, a.logintime, a.ipaddress,' \
                          ' a.macaddress, a.userproductinfo, a.interfaceproductinfo, COUNT(a.id) AS total ' \
                          'FROM (SELECT * FROM t_oper_usersession ORDER BY id DESC) a GROUP BY userid'
                elif datasource.src_model == DataSourceModel.Seat.value:
                    sql = 'SELECT seat.seat_name, sync.tradingday, sync.frontaddr, sync.seatid ' \
                          'FROM t_seat seat, t_sync_seat sync, t_capital_account ' \
                          'WHERE seat.seat_id = t_capital_account.seat_id AND sync.seatid=t_capital_account.account_id ' \
                          'AND sync.isactive = TRUE'
                datasource.source.update({'uri': uri, 'sql': sql})
            # 如果是FILE配置
            elif datasource.src_type == DataSourceType.FILE.value:
                # 去除字典中无用的key
                if 'database' in connector:
                    connector.pop('database')
                if 'charset' in connector:
                    connector.pop('charset')
                if 'port' in connector:
                    connector.pop('port')
                # 通过sysid找到对应的tradesystem
                trade_system = TradeSystem.find(**{'id': datasource.sys_id})
                # 将tradesystem中的系统信息更新到connector中
                connector.update(
                    {'login_user': trade_system.login_user, 'login_pwd': trade_system.login_pwd, 'ip': trade_system.ip})
                if trade_system:
                    uri = '{protocol}://{login_user}:{login_pwd}@{ip}:22/#{logfile}?{module}'.format(**connector)
                else:
                    raise DataNotFoundError('tradesystem not found')
                datasource.source.update({'uri': uri})
        db.session.add(datasource)
        db.session.commit()
        return RestProtocol(datasource)
