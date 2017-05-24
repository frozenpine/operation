# -*- coding: UTF-8 -*-
import logging
from os import path
from app import db
from sqlalchemy import text
from flask import (
    render_template, url_for, current_app,
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
from SysManager.executor import Executor, HttpExecutor
from SysManager.excepts import ExecuteError

class OperationListApi(Resource):
    def __init__(self):
        super(OperationListApi, self).__init__()
        self.rtn = {}

    def find_op_results(self, op):
        record = OperateRecord.query\
            .filter(OperateRecord.operation_id == op.id)\
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
                        'err_code': record.results[-1].error_code,
                        'operated_at': record.operated_at.humanize(),
                        'operator': record.operator.name,
                        'lines': record.results[-1].detail or []
                    }
                self.rtn['details'].append(dtl)
            if len(self.rtn['details']) > 0:
                self.rtn['details'][0]['enabled'] = True
            return self.rtn
        else:
            return {
                'message': 'operation group not found'
            }, 404

class OperationApi(Resource):
    def __init__(self):
        super(OperationApi, self).__init__()
        self.rtn = {}
        self.session = None
        self.op_record = OperateRecord()
        self.op_result = OperateResult()
        self.executor = None

    def ExecutionPrepare(self, operation):
        self.op_record.operation_id = operation.id
        self.op_record.operator_id = current_user.id
        self.op_record.operated_at = arrow.utcnow().to("Asia/Shanghai")
        db.session.add(self.op_record)
        db.session.commit()
        self.rtn['id'] = operation.id
        self.rtn['op_name'] = operation.name
        self.rtn['op_desc'] = operation.description
        self.rtn['checker'] = {
            'isTrue': operation.type.IsChecker(),
            'checked': False
        }
        self.rtn['interactivator'] = {
            'isTrue': operation.type.IsInteractivator(),
        }
        params = operation.detail['remote']['params']
        conf = RemoteConfig.Create(
            sub_class=operation.detail['remote']['name'],
            params=params
        )
        if session.has_key('{}:{}'.format(params.get('ip'), params.get('port'))):
            conf['session'] = session['{}:{}'.format(
                params.get('ip'),
                params.get('port')
            )]
        self.executor = Executor.Create(conf)

    def get(self, **kwargs):
        op = Operation.find(**kwargs)
        if op:
            self.ExecutionPrepare(op)
            try:
                if isinstance(op.detail['mod'], dict):
                    result = self.executor.run(op.detail['mod'])
                elif isinstance(op.detail['mod'], list):
                    result_list = []
                    for module in op.detail['mod']:
                        result_list.append(self.executor.run(module))
                    result = result_list[-1]
                else:
                    raise Exception('invalid module configuration.')
            except Exception, err:
                self.op_result.record = self.op_record
                self.op_result.error_code = 500
                self.op_result.detail = [err.message]
                self.rtn['checker']['checked'] = True
                self.rtn['err_code'] = 500
                self.rtn['output_lines'] = [err.message]
                return self.rtn, 500
            else:
                if result.return_code == 0:
                    self.rtn['err_code'] = 0
                else:
                    self.rtn['err_code'] = 10
                self.rtn['output_lines'] = result.lines
                self.op_result.op_rec_id = self.op_record.id
                self.op_result.error_code = result.return_code
                self.op_result.detail = result.lines
                return self.rtn
            finally:
                self.executor.client.close()
                db.session.add(self.op_result)
                db.session.commit()
        else:
            return {
                'message': 'operation not found'
            }, 404

    def post(self, **kwargs):
        op = Operation.find(**kwargs)
        if op:
            self.ExecutionPrepare(op)
            params = op.detail['remote']['params']
            conf = RemoteConfig.Create(
                sub_class=op.detail['remote']['name'],
                params=params
            )
            executor = Executor.Create(conf)
            try:
                result = executor.run(op.detail['mod'])
            except ExecuteError, err:
                self.op_result.record = self.op_record
                self.op_result.error_code = 500
                self.op_result.detail = json.dumps([err.message])
                self.rtn['err_code'] = 500
                self.rtn['output_lines'] = [err.message]
                return self.rtn, 500
            else:
                if result.return_code == 0:
                    self.rtn['err_code'] = 0
                else:
                    self.rtn['err_code'] = 10
                self.rtn['output_lines'] = result.lines
                self.op_result.op_rec_id = self.op_record.id
                self.op_result.error_code = result.return_code
                self.op_result.detail = json.dumps(result.lines)
                return self.rtn
            finally:
                executor.client.close()
                db.session.add(self.op_result)
                db.session.commit()
        else:
            return {
                'message': 'operation not found'
            }, 404

class OperationUIApi(Resource):
    def get(self, id):
        op = Operation.find(id=id)
        if op:
            params = op.detail['remote']['params']
            key = '{}:{}'.format(
                params.get('ip'),
                params.get('port', '8080')
            )
            if session.has_key(key):
                if arrow.utcnow().timestamp >= \
                    arrow.get(session[key].get('timeout')).timestamp:
                    session.pop(key)
                    valid_session = False
                else:
                    valid_session = session[key]['login']
            else:
                valid_session = False
            return render_template(
                'Interactivators/{}.html'.format(op.detail['mod']['name']),
                session=valid_session,
                login_user=op.detail['remote']['params']['user'],
                login_password=op.detail['remote']['params']['password'],
                captcha=op.detail['remote']['params'].get('captcha', False),
                captcha_uri=url_for('api.operation_captcha', id=op.id),
                login_uri=url_for('api.operation_login', id=op.id),
                execute_uri=url_for('api.operation_execute', id=op.id),
                csv_uri=url_for('api.operation_csv', id=op.id)
            )
        else:
            return "<h1>no ui template found</h1>"

class OperationCaptchaApi(Resource):
    def get(self, id):
        op = Operation.find(id=id)
        if op:
            params = op.detail['remote']['params']
            rsp = requests.get(
                'http://{}:{}/{}'.format(
                    params.get('ip'),
                    params.get('port', '8080'),
                    params.get('captcha_uri').lstrip('/')
                )
            )
            key = '{}:{}'.format(
                params.get('ip'),
                params.get('port', '8080')
            )
            session[key] = {
                'origin': rsp.cookies.get_dict(),
                'timeout': arrow.utcnow().shift(minutes=+30).timestamp,
                'login': False
            }
            rtn = make_response(rsp.content)
            return rtn
        else:
            return {
                'message': 'operation not found.'
            }, 404

class OperationLoginApi(Resource):
    def post(self, id):
        op = Operation.find(id=id)
        if op:
            params = op.detail['remote']['params']
            key = '{}:{}'.format(params.get('ip'), params.get('port', '8080'))
            if session.has_key(key):
                cookies = session[key]['origin']
            else:
                cookies = None
            rsp = requests.post(
                'http://{}:{}/{}'.format(
                    params.get('ip'),
                    params.get('port') or '8080',
                    params.get('login_uri').lstrip('/')
                ),
                data=request.form,
                cookies=cookies
            )
            if rsp.ok:
                rtn = rsp.json()
                session[key] = {
                    'origin': rsp.cookies.get_dict(),
                    'timeout': arrow.utcnow().shift(minutes=+30).timestamp,
                    'login': rtn['errorCode'] == 0
                }
                return rtn
            else:
                rtn = {}
                rtn['errorCode'] = rsp.status_code
                rtn['errorMsg'] = rsp.reason
                return rtn
        else:
            return {
                'message': 'operation not found.'
            }, 404

class OperationExecuteApi(Resource):
    def __init__(self):
        super(OperationExecuteApi, self).__init__()
        self.rtn = {}
        self.res = OperateResult()

    def post(self, id):
        op = Operation.find(id=id)
        if op:
            op_rec = OperateRecord()
            op_rec.operation_id = op.id
            op_rec.operator_id = current_user.id
            op_rec.operated_at = arrow.utcnow().to("Asia/Shanghai")
            db.session.add(op_rec)
            db.session.commit()
            params = op.detail['remote']['params']
            key = '{}:{}'.format(params.get('ip'), params.get('port', '8080'))
            if session.has_key(key):
                cookies = session[key]['origin']
            else:
                cookies = None
            try:
                rsp = requests.post(
                    'http://{}:{}/{}'.format(
                        params.get('ip'),
                        params.get('port', 8080),
                        op.detail['mod']['request']['uri'].lstrip('/')
                    ),
                    data=request.form,
                    cookies=cookies
                )
            except requests.HTTPError, err:
                self.res.error_code = 500
                self.res.detail = [err.message]
                return {
                    'message': err.message
                }, 500
            else:
                if rsp.ok:
                    try:
                        rsp_json = rsp.json()
                    except Exception, err:
                        self.rtn['err_code'] = 401
                        self.rtn['output_lines'] = ['please login first.']
                    else:
                        self.rtn['err_code'] = rsp_json['errorCode']
                        self.rtn['output_lines'] = format2json(rsp_json['data'])
                else:
                    self.rtn['err_code'] = rsp.status_code
                    self.rtn['output_lines'] = [rsp.reason]
            finally:
                self.rtn['id'] = op.id
                self.rtn['op_name'] = op.name
                self.rtn['op_desc'] = op.description
                self.rtn['checker'] = {
                    'isTrue': op.type.IsChecker(),
                    'checked': False
                }
                self.rtn['interactivator'] = {
                    'isTrue': True
                }
                self.res.op_rec_id = op_rec.id
                self.res.error_code = self.rtn['err_code']
                self.res.detail = self.rtn['output_lines']
                db.session.add(self.res)
                db.session.commit()
                return self.rtn
        else:
            return {
                'message': 'operation not found.'
            }, 404

def format2json(list):
    formater = u'{0:0>2d}. {1[name]:15}{1[flag]:3}'
    rtn = []
    if list:
        i = 0
        for each in json.loads(list):
            i += 1
            rtn.append(formater.format(i, each))
    return rtn

class OperationCSVApi(Resource):
    def __init__(self):
        super(OperationCSVApi, self).__init__()
        self.rtn = {}
        self.res = OperateResult()

    def post(self, id):
        op = Operation.find(id=id)
        if op:
            op_rec = OperateRecord()
            op_rec.operation_id = op.id
            op_rec.operator_id = current_user.id
            op_rec.operated_at = arrow.utcnow().to("Asia/Shanghai")
            db.session.add(op_rec)
            db.session.commit()
            params = op.detail['remote']['params']
            key = '{}:{}'.format(params.get('ip'), params.get('port', '8080'))
            if session.has_key(key):
                cookies = session[key]['origin']
            else:
                cookies = None
            file = request.files['market_csv']
            if file:
                file_path = path.join(current_app.config['UPLOAD_DIR'], 'csv', file.filename)
                file.save(file_path)
                try:
                    file_list = [
                        ('file', (
                            'marketDataCSV.csv',
                            open(file_path, 'rb'),
                            'application/vnd.ms-excel'
                        ))
                    ]
                    rsp = requests.post(
                        'http://{}:{}/{}'.format(
                            params.get('ip'),
                            params.get('port', 8080),
                            op.detail['mod']['request']['uri'].lstrip('/')
                        ),
                        files=file_list,
                        cookies=cookies
                    )
                except Exception, err:
                    self.rtn['err_code'] = 500
                    self.rtn['output_lines'] = [err.message]
                else:
                    if rsp.ok:
                        try:
                            rsp_json = rsp.json()
                        except Exception, err:
                            self.rtn['err_code'] = 401
                            self.rtn['output_lines'] = ['please login first.']
                        else:
                            self.rtn['err_code'] = rsp_json['errorCode']
                            self.rtn['output_lines'] = format2json(rsp_json['data'])
                    else:
                        self.rtn['err_code'] = rsp.status_code
                        self.rtn['output_lines'] = [rsp.reason]
                finally:
                    self.rtn['id'] = op.id
                    self.rtn['op_name'] = op.name
                    self.rtn['op_desc'] = op.description
                    self.rtn['checker'] = {
                        'isTrue': op.type.IsChecker(),
                        'checked': False
                    }
                    self.rtn['interactivator'] = {
                        'isTrue': True
                    }
                    self.res.op_rec_id = op_rec.id
                    self.res.error_code = self.rtn['err_code']
                    self.res.detail = self.rtn['output_lines']
                    db.session.add(self.res)
                    db.session.commit()
                    return self.rtn
            else:
                return {
                    'message': 'no file found.'
                }, 412
        else:
            return {
                'message': 'operation not found.'
            }
