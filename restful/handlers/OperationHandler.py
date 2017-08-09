# -*- coding: UTF-8 -*-
import datetime
import json
from os import path

import arrow
import requests
from flask import (current_app, make_response, render_template, request,
                   session, url_for)
from flask_login import current_user
from flask_restful import Resource

from SysManager.Common import AESCrypto
# from TaskManager.controller_msg import msg_dict
from TaskManager import QueueStatus, TaskStatus
from app import db, globalEncryptKey, msgQueues, taskManager, taskRequests
from app import flask_logger as logging
from app.auth.errors import (AuthError, InvalidUsernameOrPassword,
                             LoopAuthorization, NoPrivilege)
from app.auth.privileged import CheckPrivilege
from app.models import (MethodType, OperateRecord, OperateResult, Operation,
                        OperationGroup, Operator)
from restful.errors import (ApiError, ExecuteTimeOutOfRange,
                            InvalidParams, ProxyExecuteError)
from restful.protocol import RestProtocol

''' dispatchMessage = {
    DispatchResult.Dispatched: u'任务调度成功',
    DispatchResult.EmptyQueue: u'队列任务已完成',
    DispatchResult.QueueBlock: u'上一项任务未完成，无法调度新任务',
    DispatchResult.QueueMissing: u'队列不存在',
    DispatchResult.QueueNoError: u'队列无失败任务'
} '''


class OperationMixin(object):
    def __init__(self):
        self.snapshot = {}

    def find_op_status(self, op):
        if isinstance(self.snapshot, dict):
            for idx in xrange(len(self.snapshot['task_list'])):
                if op.uuid == self.snapshot['task_list'][idx]['task_uuid']:
                    if self.snapshot['task_status_list'][idx] != None:
                        return idx, TaskStatus(self.snapshot['task_status_list'][idx])
                    return idx, None
        return -1, None

    def make_operation_detail(self, op, op_session=None):
        lower, upper = op.time_range
        dtl = {
            'id': op.id,
            'uuid': op.uuid,
            'grp_uuid': op.group.uuid,
            'op_name': op.name,
            'op_desc': op.description,
            'checker': {
                'isTrue': op.operate_define.type.IsChecker(),
                'checked': False
            },
            'interactivator': {
                'isTrue': op.operate_define.type.IsInteractivator()
            },
            'time_range': {
                'lower': unicode(lower),
                'upper': unicode(upper)
            },
            'need_authorized': op.need_authorization
        }
        idx, status = self.find_op_status(op)
        if status != None:
            if status != TaskStatus.InitFail:
                if not op_session:
                    op_session = json.loads(self.snapshot['task_result_list'][idx]['session'])
                operator = Operator.find(id=op_session['operator_id'])
                dtl['operator'] = {
                    'operator_id': operator.id,
                    'operator_uuid': operator.uuid,
                    'operator_name': operator.name
                }
            if status == TaskStatus.Runnable:
                dtl['exec_code'] = -4
            elif status.IsWaiting:
                dtl['exec_code'] = -5
            elif status == TaskStatus.Running:
                dtl['exec_code'] = -2
                dtl['operated_at'] = arrow.get(op_session['operated_at']) \
                    .to('Asia/Shanghai').strftime('%Y-%m-%d %H:%M:%S')
            elif status == TaskStatus.Success or status == TaskStatus.Failed:
                dtl['exec_code'] = self.snapshot['task_result_list'][idx]['task_result']['return_code']
                dtl['output_lines'] = self.snapshot['task_result_list'][idx]['task_result']['lines']
                dtl['operated_at'] = arrow.get(op_session['operated_at']) \
                    .to('Asia/Shanghai').strftime('%Y-%m-%d %H:%M:%S')
            elif status and status.IsTimeout:
                dtl['exec_code'] = -6
            elif status == TaskStatus.Skipped:
                dtl['exec_code'] = -3
        else:
            dtl['exec_code'] = -1
        if idx > 0:
            dtl['enabled'] = (self.snapshot['task_status_list'][idx - 1]
                              == TaskStatus.Success.value) and \
                             (not self.snapshot['task_status_list'][idx]
                                  == TaskStatus.Success.value)
        elif idx == 0:
            dtl['enabled'] = not self.snapshot['task_status_list'][0] == TaskStatus.Success.value
        else:
            dtl['enabled'] = False
        return dtl

    def make_operation_list(self, op_group):
        rtn = {}
        rtn['name'] = op_group.name
        rtn['details'] = []
        rtn['system_name'] = op_group.system.name
        rtn['grp_id'] = op_group.id
        rtn['sys_id'] = op_group.system.id
        rtn['grp_uuid'] = op_group.uuid
        rtn['trigger_time'] = op_group.trigger_time
        rtn['sys_uuid'] = op_group.system.uuid
        for op in op_group.operations:
            rtn['details'].append(self.make_operation_detail(op))
        return rtn


class OperationListApi(OperationMixin, Resource):
    def __init__(self):
        super(OperationListApi, self).__init__()

    def get(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        if op_group:
            ret, self.snapshot = taskManager.snapshot(op_group.uuid)
            task_queue = {
                op_group.uuid: {
                    'group_block': True,
                    'group_info': [{
                        'task_uuid': task.uuid,
                        'detail': task.operate_define.detail,
                        'earliest': task.earliest,
                        'latest': task.latest
                    } for task in op_group.operations]
                }
            }
            now_time = datetime.datetime.today()
            try:
                trigger_hour, trigger_minute, trigger_second = \
                    op_group.trigger_time.split(':')
            except (AttributeError, ValueError):
                trigger_time = None
            else:
                trigger_time = datetime.time(
                    int(trigger_hour), int(trigger_minute), int(trigger_second)
                )
            if isinstance(self.snapshot, dict):
                create_time = datetime.datetime.strptime(
                    self.snapshot['create_time'], '%Y/%m/%d-%H:%M:%S'
                )
                if op_group.is_emergency or \
                        (now_time.day - create_time.day >= 1 and \
                                 (isinstance(trigger_time, datetime.time) and now_time.time() > trigger_time)):
                    taskManager.init(task_queue, True)
                    ret, self.snapshot = taskManager.snapshot(op_group.uuid)
                    rtn = self.make_operation_list(op_group)
                    msgQueues['tasks'].send_object(rtn)
            else:
                if isinstance(trigger_time, datetime.time) and (now_time.time() > trigger_time):
                    taskManager.init(task_queue, True)
                    ret, self.snapshot = taskManager.snapshot(op_group.uuid)
                    rtn = self.make_operation_list(op_group)
                    msgQueues['tasks'].send_object(rtn)
            return RestProtocol(self.make_operation_list(op_group))
        else:
            return RestProtocol(error_code=-1, message='Operation group not found.'), 404

    def post(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        if op_group:
            task_queue = {
                op_group.uuid: {
                    'group_block': True,
                    'group_info': [{
                        'task_uuid': task.uuid,
                        'detail': task.operate_define.detail,
                        'earliest': task.earliest,
                        'latest': task.latest
                    } for task in op_group.operations]
                }
            }
            taskManager.init(task_queue, True)
            ret, self.snapshot = taskManager.snapshot(op_group.uuid)
            rtn = self.make_operation_list(op_group)
            msgQueues['tasks'].send_object(rtn)
            return RestProtocol(rtn)
        else:
            return RestProtocol(message='Operation group not found', error_code=-1), 404


class OperationListSnapshotApi(Resource):
    def get(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        if op_group:
            ret, data = taskManager.snapshot(op_group.uuid)
            if ret == 0:
                return RestProtocol(data)
            else:
                return RestProtocol(message=data, error_code=ret)
        else:
            return RestProtocol(message='Operation group not found', error_code=-1), 404


class OperationListResumeApi(Resource):
    def get(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        if op_group:
            ret, msg = taskManager.resume(op_group.uuid)
            return RestProtocol(message=msg, error_code=ret)
        else:
            return RestProtocol(message='Operation group not found', error_code=-1), 404


class OperationListRunApi(OperationMixin, Resource):
    def __init__(self):
        super(OperationListRunApi, self).__init__()

    def get(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        if op_group:
            ret_code, data = taskManager.run_next(
                op_group.uuid,
                json.dumps({
                    'operator_id': Operator.find(login='admin').id,
                    'operated_at': unicode(arrow.utcnow())
                })
            )
            if ret_code == 0:
                ret, self.snapshot = taskManager.snapshot(op_group.uuid)
                op = Operation.find(uuid=data)
                return RestProtocol(
                    self.make_operation_detail(op),
                    message=u'任务调度成功',
                    error_code=ret_code
                )
            else:
                return RestProtocol(
                    error_code=ret_code,
                    message=data
                )
        else:
            return RestProtocol(message='Operation group not found', error_code=-1), 404


class OperationListRunAllApi(OperationMixin, Resource):
    def __init__(self):
        super(OperationListRunAllApi, self).__init__()

    def get(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        if op_group:
            if current_user.is_authenticated:
                operator = current_user
            else:
                operator = Operator.find(login='admin')
            session = {
                'operator_id': operator.id,
                'operated_at': unicode(arrow.utcnow())
            }
            ret_code, data = taskManager.run_all(
                op_group.uuid,
                json.dumps(session)
            )
            if ret_code == 0:
                op = Operation.find(uuid=data)
                ret, self.snapshot = taskManager.snapshot(op_group.uuid)
                return RestProtocol(self.make_operation_detail(op, session))
            else:
                return RestProtocol(
                    message=data,
                    error_code=ret_code
                )
        else:
            return RestProtocol(message='Operation group not found', error_code=-1), 404


class OperationApi(OperationMixin, Resource):
    def __init__(self):
        super(OperationApi, self).__init__()

    def check_privileges(self, op):
        if not op.InTimeRange():
            if not CheckPrivilege(current_user, '/api/operation/id/', MethodType.Authorize):
                raise ExecuteTimeOutOfRange(op.time_range)
        if op.need_authorization:
            if request.headers.has_key('Authorizor'):
                username, password = request.headers['Authorizor'].split('\n')
            else:
                raise NoPrivilege('Please specify an authorizor.')
            if username == current_user.login:
                raise LoopAuthorization
            else:
                authorizor = Operator.find(login=username)
                if authorizor and authorizor.verify_password(password):
                    if not CheckPrivilege(authorizor, '/api/operation/id/', MethodType.Authorize):
                        raise NoPrivilege
                    else:
                        return authorizor
                else:
                    raise InvalidUsernameOrPassword

    def get(self, **kwargs):
        op = Operation.find(**kwargs)
        if op:
            try:
                author = self.check_privileges(op)
                ret, data = taskManager.peek(op.group.uuid, op.uuid)
                if ret == 0:
                    session = {
                        'operation_id': op.id,
                        'operator_id': current_user.id,
                        'operated_at': unicode(arrow.utcnow()),
                        'authorizor_id': author and author.uuid or None,
                        'authorized_at': author and unicode(arrow.utcnow()) or None
                    }
                    taskManager.run_next(
                        op.group.uuid,
                        json.dumps(session)
                    )
                    ret, self.snapshot = taskManager.snapshot(op.group.uuid)
                    return RestProtocol(self.make_operation_detail(op, session))
                else:
                    raise ApiError(data)
            except AuthError as err:
                return RestProtocol(error_code=err.status_code, message=err.message)
            except ApiError as err:
                return RestProtocol(error_code=err.error_code, message=err.message)
        else:
            return RestProtocol(error_code=-1, message="Operation not found"), 404


class OperationCallbackApi(OperationMixin, Resource):
    def __init__(self):
        super(OperationCallbackApi, self).__init__()

    def post(self, **kwargs):
        op = Operation.find(**kwargs)
        if op:
            try:
                result = request.json
            except ValueError, err:
                logging.warning(err)
                return RestProtocol(
                    message='request header & content must be json format',
                    error_code=1
                ), 406
            else:
                ret, self.snapshot = taskManager.snapshot(op.group.uuid)
                status = TaskStatus(int(result['task_status'][0]))
                record_params = json.loads(result['session'])
                if status == TaskStatus.Running:
                    if not record_params.has_key('operation_id'):
                        record_params['operation_id'] = op.id
                    record = OperateRecord(**record_params)
                    db.session.add(record)
                    db.session.commit()
                    taskRequests[op.uuid] = record.id
                elif status == TaskStatus.Success or status == TaskStatus.Failed:
                    res = OperateResult(
                        op_rec_id=taskRequests[op.uuid],
                        error_code=result['task_result']['return_code'],
                        detail=result['task_result']['lines']
                    )
                    db.session.add(res)
                    db.session.commit()
                msgQueues['tasks'].send_object(self.make_operation_detail(op, record_params))
        else:
            return RestProtocol(error_code=-1, message='Operation not found.'), 404


class OperationUIApi(Resource):
    def get(self, id):
        op = Operation.find(id=id)
        if op:
            params = op.operate_define.detail['remote']['params']
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
                    'Interactivators/{}.html'.format(op.operate_define.detail['mod']['name']),
                    session=valid_session,
                    login_user=op.operate_define.detail['remote']['params']['user'],
                    login_password=AESCrypto.decrypt(
                        op.operate_define.detail['remote']['params']['password'],
                        globalEncryptKey
                    ),
                    captcha=op.operate_define.detail['remote']['params'].get('captcha', False),
                    captcha_uri=url_for('api.operation_captcha', id=op.id),
                    login_uri=url_for('api.operation_login', id=op.id),
                    execute_uri=url_for('api.operation_execute', id=op.id),
                    csv_uri=url_for('api.operation_csv', id=op.id)
                )
            else:
                return render_template(
                    'Interactivators/{}.html'.format(op.operate_define.detail['mod']['name']),
                    session=valid_session,
                    login_user=op.operate_define.detail['remote']['params']['user'],
                    login_password=op.operate_define.detail['remote']['params']['password'],
                    captcha=op.operate_define.detail['remote']['params'].get('captcha', False),
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
            params = op.operate_define.detail['remote']['params']
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
            params = op.operate_define.detail['remote']['params']
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
            except ApiError, err:
                return {
                    'errorCode': err.error_code,
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


class OperationExecuteApi(OperationApi):
    def post(self, id):
        op = Operation.find(id=id)
        if op:
            self.ExecutionPrepare(op)
            params = op.operate_define.detail['remote']['params']
            key = '{}:{}'.format(params.get('ip'), params.get('port', '8080'))
            if session.has_key(key):
                self.session = session[key]['origin']
            try:
                if not op.InTimeRange():
                    raise ExecuteTimeOutOfRange(op.time_range)
                module = op.operate_define.detail['mod']['request']
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
                if op.operate_define.detail.get('skip'):
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
                                           op.operate_define.type.IsChecker() and \
                                           not op.operate_define.type.IsBatcher()
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


class OperationCSVApi(OperationApi):
    def post(self, id):
        op = Operation.find(id=id)
        if op:
            self.ExecutionPrepare(op)
            params = op.operate_define.detail['remote']['params']
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
                            op.operate_define.detail['mod']['request']['uri'].lstrip('/')
                        ),
                        files=file_list,
                        cookies=self.session
                    )
                    result = _handlerJsonResponse(rsp)
                except ApiError, err:
                    self.op_result.error_code = err.status_code
                    self.op_result.detail = [err.message]
                    if op.operate_define.detail.get('skip'):
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
                                               op.operate_define.type.IsChecker() and \
                                               not op.operate_define.type.IsBatcher()
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
