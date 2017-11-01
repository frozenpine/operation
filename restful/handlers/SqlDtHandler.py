# -*- coding: UTF-8 -*-
import re

import arrow
import gevent
from flask import current_app
from flask_restful import Resource

from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.exc import NoSuchColumnError

from app import globalEncryptKey
from app.models import DataSource, DataSourceModel, DataSourceType, TradeSystem
from restful.protocol import RestProtocol
from SysManager.Common import AESCrypto


def _decrypt(match):
    return match.group(1) + \
           AESCrypto.decrypt(
               match.group(2),
               globalEncryptKey
           ) + \
           match.group(3)

class SqlApi(Resource):
    def __init__(self):
        self.dt_list = {}
        self.rtn = []
        self.checker = []
        self.system_list = []
        self.app_context = current_app.app_context()

    def find_systems(self, sys):
        if len(sys.processes) > 0:
            self.system_list.append(sys)
        if len(sys.child_systems) > 0:
            for child_sys in sys.child_systems:
                self.find_systems(child_sys)

    def find_tables(self, sys):
        self.find_systems(sys)
        sources = DataSource.query.filter(
            DataSource.src_type == DataSourceType.SQL,
            DataSource.src_model == DataSourceModel.Custom,
            DataSource.sys_id.in_([x.id for x in self.system_list]),
            DataSource.disabled == False
        ).all()
        for src in sources:
            if globalEncryptKey:
                uri = re.sub(
                    '^(.+://[^:]+:)([^@]+)(@.+)$',
                    _decrypt,
                    src.source['uri']
                )
            else:
                uri = src.source['uri']
            if not self.dt_list.has_key(uri):
                self.dt_list[uri] = []
            self.dt_list[uri].append(src)

    def get_datetable(self, uri, dts):
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
            for dt in dts:
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
                    data_table['update_time'] = arrow.utcnow()\
                            .to(current_app.config['TIME_ZONE']).format('HH:mm:ss')
                rtn['data_tables'].append(data_table)
            self.rtn.append(rtn)

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_tables(sys)
            for (k, v) in self.dt_list.items():
                self.checker.append(gevent.spawn(self.get_datetable, k, v))
                # self.get_datetable(k, v)
            # gevent.sleep(0)
            gevent.joinall(self.checker)
            return RestProtocol(self.rtn)
        else:
            return RestProtocol(message='System not found', error_code=-1), 404
