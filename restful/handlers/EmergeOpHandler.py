# -*- coding: UTF-8 -*-
import json
import logging

import arrow
import requests
from flask import (current_app, make_response, render_template, request,
                   session, url_for)
from flask_login import current_user
from flask_restful import Resource
from sqlalchemy import text

from app import db
from app.auth.errors import (AuthError, InvalidUsernameOrPassword,
                             LoopAuthorization, NoPrivilege)
from app.auth.privileged import CheckPrivilege
from app.models import (MethodType, EmergeOpRecord, EmergeOpResult,
                        OperationBook, Operator, ScriptType, TradeSystem)
from restful.errors import (ApiError, ExecuteError, ExecuteTimeOutOfRange,
                            InvalidParams, ProxyExecuteError)
from SysManager.Common import AESCrypto
from SysManager.configs import RemoteConfig, Result, SSHConfig
from SysManager.excepts import ExecuteError
from SysManager.executor import Executor, HttpExecutor

class  EmergeOpListApi(Resource):
    def __init__(self):
        super(EmergeOpListApi, self).__init__()
        self.emerge_groups = {}

    def find_operations(self, sys):
        emerge_ops = OperationBook.query.filter(
            OperationBook.sys_id == sys.id,
            OperationBook.is_emergecy == True
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
                    'operated_at': record.operated_at.humanize(),
                    'operator': record.operator.name,
                    'lines': record.results[-1].detail or []
                }
            self.emerge_groups[op.catalog]['details'].append(dtl)

    def find_op_record(self, op):
        record = EmergeOpRecord.query\
            .filter(EmergeOpRecord.operation_id == op.id)\
                .order_by(EmergeOpRecord.operated_at.desc()).first()
        return record

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_operations(sys)
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
        self.op_record.operation_id = emerge_op.id
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
