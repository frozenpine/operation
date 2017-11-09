# -*- coding: UTF-8 -*-
import json

import arrow
import requests
from flask import (current_app, make_response, render_template, request,
                   session, url_for)
from flask_login import current_user
from flask_restful import Resource

from SysManager.Common import AESCrypto
from SysManager.configs import RemoteConfig
from SysManager.executor import Executor
from app import db, globalEncryptKey
from app.auth.privileged import CheckPrivilege
from app.models import (EmergeOpRecord, EmergeOpResult, MethodType,
                        OperationBook, TradeSystem)
from restful.errors import (ApiError, ExecuteTimeOutOfRange,
                            InvalidParams, ProxyExecuteError)


class EmergeOpListApi(Resource):
    def __init__(self):
        super(EmergeOpListApi, self).__init__()
        self.emerge_groups = {}
        self.system_list = []

    def find_systems(self, sys):
        self.system_list.append(sys.id)
        for child_sys in sys.child_systems:
            self.find_systems(child_sys)

    def find_operations(self):
        emerge_ops = OperationBook.query.filter(
            OperationBook.sys_id.in_((self.system_list))
        ).order_by(OperationBook.order).all()
        for op in emerge_ops:
            record = self.find_op_record(op)
            if not self.emerge_groups.has_key(op.catalog):
                self.emerge_groups[op.catalog] = {
                    'name': op.catalog.name,
                    'details': []
                }
            dtl = {
                'id': op.id,
                'op_name': op.name,
                'op_desc': op.description,
                'sys_id': op.sys_id,
                'err_code': -1,
                'interactivator': {
                    'isTrue': op.type.IsInteractivator()
                }
            }
            if record:
                dtl['his_results'] = {
                    'err_code': record.results[-1].error_code,
                    'operated_at': record.operated_at.to(current_app.config['TIME_ZONE']).strftime('%Y-%m-%d %H:%M:%S'),
                    'operator': record.operator.name,
                    'lines': record.results[-1].detail or []
                }
            self.emerge_groups[op.catalog]['details'].append(dtl)

    def find_op_record(self, op):
        record = EmergeOpRecord.query \
            .filter(EmergeOpRecord.emergeop_id == op.id) \
            .order_by(EmergeOpRecord.operated_at.desc()).first()
        return record

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_systems(sys)
            self.find_operations()
            return [
                self.emerge_groups[key] for key in sorted(
                    self.emerge_groups.keys(), key=lambda key: key.order
                )
            ]
        else:
            return {
                       'message': 'system not found.'
                   }, 404


class EmergeOpApi(Resource):
    def __init__(self):
        super(EmergeOpApi, self).__init__()
        self.rtn = {}
        self.session = None
        self.op_record = EmergeOpRecord()
        self.op_result = EmergeOpResult()
        self.executor = None

    def ExecutionPrepare(self, emerge_op):
        self.op_record.emergeop_id = emerge_op.id
        self.op_record.operator_id = current_user.id
        self.op_record.operated_at = arrow.now()
        db.session.add(self.op_record)
        db.session.commit()
        self.op_result.record = self.op_record
        self.rtn['id'] = emerge_op.id
        self.rtn['op_name'] = emerge_op.name
        self.rtn['op_desc'] = emerge_op.description
        self.rtn['interactivator'] = {
            'isTrue': emerge_op.type.IsInteractivator()
        }
        params = emerge_op.detail['remote']['params']
        conf = RemoteConfig.Create(emerge_op.detail['remote']['name'], params)
        self.executor = Executor.Create(conf)

    def post(self, **kwargs):
        emerge_op = OperationBook.find(**kwargs)
        if emerge_op:
            self.ExecutionPrepare(emerge_op)
            module = emerge_op.detail['mod']
            try:
                if isinstance(module, dict):
                    result = self.executor.run(module)
                elif isinstance(module, list):
                    for mod in module:
                        result = self.executor.run(mod)
                        if result.return_code != 0:
                            break
            except Exception:
                self.op_result.error_code = 500
                self.op_result.lines = [u'发生未知错误，执行失败']
            else:
                self.op_result.error_code = result.return_code
                self.op_result.detail = result.lines
            finally:
                self.executor.client.close()
                db.session.add(self.op_result)
                db.session.commit()
                self.rtn['err_code'] = self.op_result.error_code
                self.rtn['output_lines'] = self.op_result.detail
                return self.rtn
        else:
            return {
                       'message': 'operation not found.'
                   }, 404


class EmergeOpUIApi(Resource):
    def get(self, id):
        op = OperationBook.find(id=id)
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
            if globalEncryptKey:
                return render_template(
                    'Interactivators/{}.html'.format(op.detail['mod']['name']),
                    session=valid_session,
                    login_user=op.detail['remote']['params']['user'],
                    login_password=AESCrypto.decrypt(
                        op.detail['remote']['params']['password'],
                        globalEncryptKey
                    ),
                    captcha=op.detail['remote']['params'].get('captcha', False),
                    captcha_uri=url_for('api.emergeop_captcha', id=op.id),
                    login_uri=url_for('api.emergeop_login', id=op.id),
                    execute_uri=url_for('api.emergeop_execute', id=op.id),
                    csv_uri=url_for('api.emergeop_csv', id=op.id)
                )
            else:
                return render_template(
                    'Interactivators/{}.html'.format(op.detail['mod']['name']),
                    session=valid_session,
                    login_user=op.detail['remote']['params']['user'],
                    login_password=op.detail['remote']['params']['password'],
                    captcha=op.detail['remote']['params'].get('captcha', False),
                    captcha_uri=url_for('api.emergeop_captcha', id=op.id),
                    login_uri=url_for('api.emergeop_login', id=op.id),
                    execute_uri=url_for('api.emergeop_execute', id=op.id),
                    csv_uri=url_for('api.emergeop_csv', id=op.id)
                )
        else:
            return "<h1>no ui template found</h1>"


class EmergeOpCaptchaApi(Resource):
    def get(self, id):
        op = OperationBook.find(id=id)
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


class EmergeOpLoginApi(Resource):
    def post(self, id):
        op = OperationBook.find(id=id)
        if op:
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
                        params.get('port') or '8080',
                        params.get('login_uri').lstrip('/')
                    ),
                    data=request.form,
                    cookies=cookies
                )
                result = _handlerJsonResponse(rsp)
            except ApiError as err:
                return {
                    'errorCode': err.status_code,
                    'errorMsg': err.message
                }  # 模拟HTTP接口的返回数据，用于前端UI模块正确显示数据。
            else:
                session[key] = {
                    'origin': rsp.cookies.get_dict(),
                    'timeout': arrow.utcnow().shift(minutes=+30).timestamp,
                    'login': result['errorCode'] == 0
                }
                return result
        else:
            return {
                       'message': 'operation not found.'
                   }, 404


class EmergeOpExecuteApi(EmergeOpListApi):
    def post(self, id):
        op = OperationBook.find(id=id)
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
            except ApiError as err:
                self.op_result.error_code = err.status_code
                self.op_result.detail = [err.message]
                if op.detail.get('skip'):
                    self.rtn['skip'] = True
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
                raise ProxyExecuteError(rsp_json['errorMsg'])
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


class EmergeOpCSVApi(EmergeOpListApi):
    def post(self, id):
        op = OperationBook.find(id=id)
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
                    result = _handlerJsonResponse(rsp)
                except ApiError as err:
                    self.op_result.error_code = err.status_code
                    self.op_result.detail = [err.message]
                    if op.detail.get('skip'):
                        self.rtn['skip'] = True
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
                           'message': 'no file found.'
                       }, 412
        else:
            return {
                       'message': 'operation not found.'
                   }, 404
