# -*- coding: UTF-8 -*-
import logging
from os import path
from app import db
from app.auth.privileged import CheckPrivilege
from app.auth.errors import (
    AuthError, InvalidUsernameOrPassword, NoPrivilege,
    LoopAuthorization
)
from restful.errors import (
    ApiError, ExecuteTimeOutOfRange, InvalidParams,
    ExecuteError, ProxyExecuteError
)
from sqlalchemy import text
from flask import (
    render_template, url_for, current_app,
    make_response, request, session
)
from flask_login import current_user
from flask_restful import Resource
from app.models import (
    OperationGroup, Operation, ScriptType, Operator,
    OperateRecord, OperateResult, MethodType
)
from app.auth.privileged import CheckPrivilege
import arrow
import json
import requests
from SysManager.configs import Result, RemoteConfig, SSHConfig
from SysManager.executor import Executor, HttpExecutor
from SysManager.excepts import ExecuteError
from SysManager.Common import AESCrypto

class OperationListApi(Resource):
    def __init__(self):
        super(OperationListApi, self).__init__()
        self.rtn = {}

    def find_op_record(self, op):
        record = OperateRecord.query\
            .filter(OperateRecord.operation_id == op.id)\
                .order_by(OperateRecord.operated_at.desc()).first()
        if record and \
            record.operated_at.timestamp > \
                arrow.get(arrow.now().strftime('%Y-%m-%d')).timestamp:
            return record.results[-1].error_code == 0, record
        else:
            return False, None

    def get(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        if op_group:
            self.rtn['name'] = op_group.name
            self.rtn['details'] = []
            self.rtn['system_name'] = op_group.system.name
            for op in op_group.operations:
                skip, record = self.find_op_record(op)
                lower, upper = op.time_range
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
                    'time_range': {
                        'lower': unicode(lower or 'anytime'),
                        'upper': unicode(upper or 'anytime')
                    },
                    'need_authorized': op.detail.has_key('need_authorized') and \
                        op.detail['need_authorized'],
                    'skip': skip
                }
                if record:
                    dtl['enabled'] = True
                    dtl['re_enter'] = (
                        op.type.IsChecker() and \
                            not op.type.IsBatcher()
                    ) or not skip \
                        or CheckPrivilege(
                            current_user,
                            '/api/operation/id/',
                            MethodType.ReExecute
                        )
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
        self.op_record.operated_at = arrow.now()
        db.session.add(self.op_record)
        db.session.commit()
        self.op_result.record = self.op_record
        lower, upper = operation.time_range
        self.rtn['id'] = operation.id
        self.rtn['op_name'] = operation.name
        self.rtn['op_desc'] = operation.description
        self.rtn['enabled'] = True
        self.rtn['checker'] = {
            'isTrue': operation.type.IsChecker(),
            'checked': False
        }
        self.rtn['interactivator'] = {
            'isTrue': operation.type.IsInteractivator(),
        }
        self.rtn['time_range'] = {
            'lower': unicode(lower or 'anytime'),
            'upper': unicode(upper or 'anytime')
        }
        self.rtn['need_authorized'] = operation.detail.has_key('need_authorized') and \
            operation.detail['need_authorized']
        params = operation.detail['remote']['params']
        conf = RemoteConfig.Create(operation.detail['remote']['name'], params)
        key = '{}:{}'.format(
            params.get('ip'),
            params.get('port', '8080')
        )
        if session.has_key(key):
            self.session = session[key]['origin']
        self.executor = Executor.Create(conf)

    def post(self, **kwargs):
        op = Operation.find(**kwargs)
        if op:
            self.ExecutionPrepare(op)
            try:
                if not op.InTimeRange():
                    raise ExecuteTimeOutOfRange(op.time_range)
                if request.json:
                    if request.json['authorizor'] == current_user.login:
                        raise LoopAuthorization
                    else:
                        authorizor = Operator.find(login=request.json['authorizor'])
                        if authorizor and authorizor.verify_password(request.json['password']):
                            if not CheckPrivilege(
                                    authorizor,
                                    '/api/operation/id/',
                                    MethodType.Authorize
                            ):
                                raise NoPrivilege
                            else:
                                self.op_record.authorizor_id = authorizor.id
                                self.op_record.authorized_at = arrow.now()
                                db.session.add(self.op_record)
                                db.session.commit()
                        else:
                            raise InvalidUsernameOrPassword
                if isinstance(op.detail['mod'], dict):
                    result = self.executor.run(op.detail['mod'])
                elif isinstance(op.detail['mod'], list):
                    for module in op.detail['mod']:
                        result = self.executor.run(module)
                        if result.return_code != 0:
                            break
                else:
                    raise ApiError('invalid module configuration.')
            except AuthError, err:
                self.op_result.error_code = err.status_code
                self.op_result.detail = [err.message]
            except ApiError, err:
                self.op_result.error_code = err.status_code
                self.op_result.detail = [err.message]
            else:
                self.op_result.error_code = result.return_code
                self.op_result.detail = result.lines
            finally:
                self.executor.client.close()
                db.session.add(self.op_result)
                db.session.commit()
                self.rtn['err_code'] = self.op_result.error_code
                self.rtn['output_lines'] = self.op_result.detail
                self.rtn['re_enter'] = (
                    op.type.IsChecker() and \
                        not op.type.IsBatcher() or self.op_result.error_code != 0
                ) or CheckPrivilege(
                    current_user,
                    '/api/operation/id/',
                    MethodType.ReExecute
                )
                return self.rtn
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
            if current_app.config['GLOBAL_ENCRYPT']:
                return render_template(
                    'Interactivators/{}.html'.format(op.detail['mod']['name']),
                    session=valid_session,
                    login_user=op.detail['remote']['params']['user'],
                    login_password=AESCrypto.decrypt(
                        op.detail['remote']['params']['password'],
                        current_app.config['SECRET_KEY']
                    ),
                    captcha=op.detail['remote']['params'].get('captcha', False),
                    captcha_uri=url_for('api.operation_captcha', id=op.id),
                    login_uri=url_for('api.operation_login', id=op.id),
                    execute_uri=url_for('api.operation_execute', id=op.id),
                    csv_uri=url_for('api.operation_csv', id=op.id)
                )
            else:
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

class OperationExecuteApi(OperationApi):
    def post(self, id):
        op = Operation.find(id=id)
        if op:
            self.ExecutionPrepare(op)
            params = op.detail['remote']['params']
            key = '{}:{}'.format(params.get('ip'), params.get('port', '8080'))
            if session.has_key(key):
                self.session = session[key]['origin']
            try:
                if not op.InTimeRange():
                    raise ExecuteTimeOutOfRange(op.time_range)
                module = op.detail['mod']['request']
                if isinstance(module, dict):
                    rsp = getattr(requests, module['method'])(
                        'http://{}:{}/{}'.format(
                            params.get('ip'),
                            params.get('port', 8080),
                            module['uri'].lstrip('/')
                        ),
                        data=request.form,
                        cookies=self.session
                    )
                    result = _handlerJsonResponse(rsp)
                elif isinstance(module, list):
                    for mod in module:
                        if mod.has_key('params'):
                            data = mod['params']
                        else:
                            data = request.form
                        rsp = getattr(requests, mod['method'])(
                            'http://{}:{}/{}'.format(
                                params.get('ip'),
                                params.get('port', 8080),
                                mod['uri'].lstrip('/')
                            ),
                            data=data,
                            cookies=self.session
                        )
                        result = _handlerJsonResponse(rsp)
                        if result['errorCode'] != 0:
                            break
            except ApiError, err:
                self.op_result.error_code = err.status_code
                self.op_result.detail = [err.message]
            else:
                if result['errorCode'] != 0:
                    self.op_result.error_code = 10
                else:
                    self.op_result.error_code = 0
                self.op_result.detail = _format2json(result['data'])
            finally:
                db.session.add(self.op_result)
                db.session.commit()
                self.rtn['err_code'] = self.op_result.error_code
                self.rtn['output_lines'] = self.op_result.detail
                self.rtn['re_enter'] = (
                    op.type.IsChecker() and \
                        not op.type.IsBatcher()
                ) or CheckPrivilege(
                    current_user,
                    '/api/operation/id/',
                    MethodType.ReExecute
                )
                return self.rtn
        else:
            return {
                'message': 'operation not found.'
            }, 404

def _handlerJsonResponse(response):
    if response.ok:
        try:
            rsp_json = response.json()
        except:
            raise InvalidParams
        else:
            if rsp_json['errorCode'] != 0:
                raise ProxyExecuteError
            else:
                return rsp_json
    else:
        raise ApiError('request failed.')

def _format2json(data):
    formater = u'{0:0>2d}. {1[name]:15}{1[flag]:3}'
    rtn = []
    if data:
        i = 0
        js_data = json.loads(data)
        if isinstance(js_data, list):
            for each in json.loads(data):
                i += 1
                rtn.append(formater.format(i, each))
        else:
            rtn.append(data)
    return rtn

class OperationCSVApi(OperationApi):
    def post(self, id):
        op = Operation.find(id=id)
        if op:
            self.ExecutionPrepare(op)
            params = op.detail['remote']['params']
            key = '{}:{}'.format(params.get('ip'), params.get('port', '8080'))
            if session.has_key(key):
                self.session = session[key]['origin']
            file = request.files['market_csv']
            if file:
                file_path = path.join(current_app.config['UPLOAD_DIR'], 'csv', file.filename)
                file.save(file_path)
                try:
                    if not op.InTimeRange():
                        raise Exception(
                            'execution time out of range[{range[0]} ~ {range[1]}].'.format(
                                range=op.time_range
                            )
                        )
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
                        cookies=self.session
                    )
                except Exception, err:
                    self.op_result.error_code = 500
                    self.op_result.detail = [err.message]
                else:
                    if rsp.ok:
                        try:
                            rsp_json = rsp.json()
                        except Exception, err:
                            self.op_result.error_code = 401
                            self.op_result.detail = ['please login first.']
                        else:
                            if rsp_json['errorCode'] != 0:
                                self.op_result.error_code = 10
                            else:
                                self.op_result.error_code = 0
                            self.op_result.detail = _format2json(rsp_json['data'])
                    else:
                        self.op_result.error_code = rsp.status_code
                        self.op_result.detail = [rsp.reason]
                finally:
                    db.session.add(self.op_result)
                    db.session.commit()
                    self.rtn['err_code'] = self.op_result.error_code
                    self.rtn['output_lines'] = self.op_result.detail
                    self.rtn['re_enter'] = (
                        op.type.IsChecker() and \
                            not op.type.IsBatcher()
                    ) or CheckPrivilege(
                        current_user,
                        '/api/operation/id/',
                        MethodType.ReExecute
                    )
                    return self.rtn
            else:
                return {
                    'message': 'no file found.'
                }, 412
        else:
            return {
                'message': 'operation not found.'
            }, 404
