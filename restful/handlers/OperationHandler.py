# -*- coding: UTF-8 -*-
import logging
from app import db
from sqlalchemy import text
from flask import (
    render_template, url_for,
    make_response, request, session
)
from flask_login import current_user
from flask_restful import Resource
from app.models import (
    OperationGroup, Operation, ScriptType,
    OperateRecord, OperateResult
)
import arrow
import json
import requests
from SysManager.configs import Result, RemoteConfig, SSHConfig
from SysManager.executor import Executor
from SysManager.excepts import ExecuteError

class OperationListApi(Resource):
    def __init__(self):
        super(OperationListApi, self).__init__()
        self.rtn = {}

    def find_op_results(self, op):
        record = OperateRecord.query\
            .filter(OperateRecord.operation_id==op.id)\
                .order_by(OperateRecord.operated_at.desc()).first()
        if record:
            return record.operated_at.timestamp > \
                arrow.get(arrow.now().strftime('%Y-%m-%d')).timestamp, record
        else:
            return False, None

    def get(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        if op_group:
            self.rtn['name'] = op_group.name
            self.rtn['details'] = []
            for op in op_group.operations:
                skip, record = self.find_op_results(op)
                dtl = {
                    'id': op.id,
                    'op_name': op.name,
                    'op_desc': op.description,
                    'err_code': -1,
                    'enabled': False,
                    're_enter': True,
                    'checker': {
                        'isTrue': op.type.IsChecker(),
                        'checked': False
                    },
                    'interactivator': {
                        'isTrue': op.type.IsInteractivator()
                    },
                    'skip': skip
                }
                if skip:
                    dtl['his_results'] = {
                        'operated_at': record.operated_at.humanize(),
                        'operator': record.operator.name,
                        'lines': json.loads(record.results[-1].detail)
                    }
                if op.type.IsInteractivator():
                    dtl['interactivator']['template'] = render_template(
                        'Interactivators/{}.html'.format('quantdo'),
                        login_user=op.detail['remote']['params']['user'],
                        login_password=op.detail['remote']['params']['password'],
                        captcha=op.detail['remote']['params'].get('captcha', False),
                        captcha_uri=url_for('api.operation_captcha', id=op.id),
                        login_uri=url_for('api.operation_login', id=op.id)
                    )
                self.rtn['details'].append(dtl)
            if len(self.rtn['details']) > 0:
                self.rtn['details'][0]['enabled'] = True
            return self.rtn
        else:
            return {
                'message': 'operation group not found'
            }, 404

class OperationApi(Resource):
    def get(self, **kwargs):
        op = Operation.find(**kwargs)
        rtn = {}
        if op:
            op_rec = OperateRecord()
            op_rec.operation_id = op.id
            op_rec.operator_id = current_user.id
            op_rec.operated_at = arrow.utcnow().to("Asia/Shanghai")
            db.session.add(op_rec)
            db.session.commit()
            rtn['id'] = op.id
            rtn['op_name'] = op.name
            rtn['op_desc'] = op.description
            rtn['checker'] = {
                'isTrue': op.type.IsChecker(),
                'checked': False
            }
            conf = RemoteConfig.Create(
                sub_class=op.detail['remote']['name'],
                params=op.detail['remote']['params']
            )
            executor = Executor.Create(conf)
            try:
                result = executor.run(op.detail['mod'])
            except ExecuteError, err:
                res = OperateResult()
                res.op_rec_id = op_rec.id
                res.error_code = 500
                res.detail = json.dumps([err.message])
                rtn['err_code'] = 500
                rtn['output_lines'] = [err.message]
                db.session.add(res)
                db.session.commit()
                return rtn, 500
            else:
                if result.return_code == 0:
                    rtn['err_code'] = 0
                else:
                    rtn['err_code'] = 10
                rtn['output_lines'] = result.lines
                res = OperateResult()
                res.op_rec_id = op_rec.id
                res.error_code = result.return_code
                res.detail = json.dumps(result.lines)
                db.session.add(res)
                db.session.commit()
                return rtn
            finally:
                executor.client.close()
        else:
            return {
                'message': 'operation not found'
            }, 404

class OperationCaptchaApi(Resource):
    def get(self, id):
        op = Operation.find(id=id)
        if op:
            '''
            conf = RemoteConfig.Create(
                op.detail['remote']['name'],
                op.detail['remote']['params']
            )
            executor = Executor.Create(conf)
            rsp = executor.Captcha(conf)
            return make_response(rsp.content)
            '''
            params = op.detail['remote']['params']
            req = requests.Session()
            rsp = req.get(
                'http://{}:{}/{}'.format(
                    params.get('ip'),
                    params.get('port') or '8080',
                    params.get('captcha_uri').lstrip('/')
                )
            )
            session['http_token'] = rsp.cookies['token']
            rtn = make_response(rsp.content)
            return rtn

class OperationLoginApi(Resource):
    def post(self, id):
        op = Operation.find(id=id)
        if op:
            req = requests.Session()
            if session.has_key('http_token'):
                cookie = {'token': session['http_token']}
            else:
                cookie = None
            params = op.detail['remote']['params']
            rsp = req.post(
                'http://{}:{}/{}'.format(
                    params.get('ip'),
                    params.get('port') or '8080',
                    params.get('login_uri')
                ),
                data={
                    'params': json.dumps({
                        'userName': request.values.get('userName'),
                        'password': request.values.get('password'),
                        'verification_code': request.values.get('verification_code')
                    })
                },
                cookies=cookie
            )
            rtn = rsp.json()
            next_trading_day = db.session.execute(
                text(
                    "\
                    SELECT trade_calendar.full_date \
                    FROM trade_calendar \
                    WHERE trade_calendar.full_date>'{}' \
                        AND trade_calendar.is_trade=1 \
                    LIMIT 1\
                    ".format(arrow.utcnow().to('Asia/Shanghai').format('YYYYMMDD'))
                )
            ).first()[0]
            rtn['next_trading_day'] = next_trading_day
            return rtn
