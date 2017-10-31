# -*- coding: UTF-8 -*-
import re

import arrow
import gevent
from flask_restful import Resource, request

from app import globalEncryptKey, msgQueues
from app.models import DataSource, DataSourceModel, DataSourceType, TradeSystem
from restful.protocol import RestProtocol
from SysManager.Common import AESCrypto
from SysManager.configs import SSHConfig, WinRmConfig
from SysManager.executor import Executor


def _decrypt(match):
    return match.group(1) + \
           AESCrypto.decrypt(
               match.group(2),
               globalEncryptKey
           ) + \
           match.group(3)

class LogApi(Resource):
    def __init__(self):
        self.log_list = {}
        self.rtn = []
        self.checker = []

    def post(self):
        msg = request.json['msg']
        # source = request.headers.get('src')
        # topic = request.headers.get('topic')
        # print msg, source
        '''
        if topic:
            print topic
            msgQueues[topic].put_message(msg)
        else:
        '''
        msgQueues['public'].send_message(msg.encode('utf-8'))

    def find_logs(self, sys):
        sources = DataSource.query.filter(
            DataSource.src_type == DataSourceType.FILE,
            DataSource.src_model == DataSourceModel.Custom,
            DataSource.sys_id == sys.id,
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
            uri = uri.split('#')
            svr = uri[0].rstrip('/')
            log_define = uri[1]
            if not self.log_list.has_key(svr):
                self.log_list[svr] = []
            self.log_list[svr].append({
                'formatter': src.source.get('formatter'),
                'msg_pattern': src.source.get('msg_pattern'),
                'key_words': src.source['key_words'],
                'log_define': log_define
            })

    def check_log(self, uri, datas):
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
        for data in datas:
            logfile, module = data.pop('log_define').split('?')
            mod = {}
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
            data_res = {'results': result.lines, 'log_file': logfile.rstrip('/')}
            data_res.update(data)
            res['logs'].append(data_res)
        self.rtn.append(res)

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_logs(sys)
            for (k, v) in self.log_list.items():
                self.checker.append(gevent.spawn(self.check_log, k, v))
            # gevent.sleep(0)
            gevent.joinall(self.checker)
            return RestProtocol(self.rtn)
        else:
            return RestProtocol(message='System not found', error_code=-1), 404
