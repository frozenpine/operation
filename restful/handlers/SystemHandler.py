# -*- coding: UTF-8 -*-
from flask_restful import Resource
from app.models import TradeSystem, DataSource, DataSourceType, OperationBook, EmergeOpRecord, MethodType
from app import db
from flask import request
from werkzeug.exceptions import BadRequest
from ..errors import DataNotJsonError, DataUniqueError, DataNotNullError, DataNotMatchError, ApiError
import json
import re
from ..protocol import RestProtocol


class SystemApi(Resource):
    def __init__(self):
        super(SystemApi, self).__init__()
        self.pattern = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')

    def get(self, **kwargs):
        system = TradeSystem.find(**kwargs)
        if system:
            return RestProtocol(system)
        else:
            return RestProtocol(message='System not found', error_code=-1), 404

    def put(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            try:
                data = request.get_json(force=True)
                if data.get('name'):
                    if sys.name != data.get('name') and TradeSystem.find(name=data.get('name')):
                        raise DataUniqueError
                if data.get('ip'):
                    if not self.pattern.match(data.get('ip')):
                        raise DataTypeError('Please enter a valid IP address.')
            except BadRequest:
                return RestProtocol(DataNotJsonError())
            except ApiError as e:
                return RestProtocol(e)
            else:
                sys.name = data.get('name', sys.name)
                sys.user = data.get('user', sys.user)
                sys.password = data.get('password', sys.password)
                sys.ip = data.get('ip', sys.ip)
                sys.description = data.get('description', sys.description)
                sys.version = data.get('version', sys.version)
                sys.type_id = data.get('type_id', sys.type_id)
                sys.base_dir = data.get('base_dir', sys.base_dir)
                sys.vendor_id = data.get('vendor_id', sys.vendor_id)
                sys.parent_sys_id = data.get('parent_sys_id', sys.parent_sys_id)
                sys.disabled = data.get('disabled', sys.disabled)
                for op in sys.operation_book:
                    details = json.loads(json.dumps(op.detail))
                    params = details['remote']['params']
                    params['ip'] = sys.ip
                    params['user'] = sys.user
                    params['password'] = sys.login_pwd
                    op.detail = details
                    db.session.add(op)
                for ds in DataSource.query.filter(
                                DataSource.src_type == DataSourceType.FILE
                ):
                    source = json.loads(json.dumps(ds.source))
                    source['uri'] = re.sub(
                        '^(?P<header>[^:]+)://([^:]+):([^@]+)@([^:]+):(?P<tailer>.+)$',
                        lambda matchs: matchs.group('header') + \
                                       "://" + sys.user + ":" + sys.login_pwd + \
                                       "@" + sys.ip + ":" + matchs.group('tailer'),
                        source['uri']
                    )
                    ds.source = source
                    db.session.add(ds)
                db.session.add(sys)
                db.session.commit()
                return RestProtocol(sys)
        else:
            return RestProtocol(message='System not found', error_code=-1), 404


class SystemListApi(Resource):
    def __init__(self):
        super(SystemListApi, self).__init__()
        self.not_null_list = ['name', 'user', 'password', 'ip']
        self.pattern = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')

    def get(self):
        systems = TradeSystem.query.filter(
			TradeSystem.parent_sys_id == None,
			TradeSystem.disabled == False
		).all()
        return RestProtocol(systems)

    def post(self):
        system = []
        result_list = []
        try:
            data = request.get_json(force=True)
            for param in self.not_null_list:
                if not data.get(param):
                    raise DataNotNullError('Please input {}'.format(param))
            if TradeSystem.find(name=data.get('name')):
                raise DataUniqueError
            if not self.pattern.match(data.get('ip')):
                raise DataTypeError('Please enter a valid IP address.')
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        except ApiError as e:
            return RestProtocol(e)
        else:
            system = TradeSystem()
            system.name = data.get('name')
            system.description = data.get('description')
            system.type_id = data.get('type_id')
            system.version = data.get('version')
            system.ip = data.get('ip')
            system.user = data.get('user')
            system.password = data.get('password')
            system.base_dir = data.get('base_dir')
            system.vendor_id = data.get('vendor_id')
            system.parent_sys_id = data.get('parent_sys_id')
            db.session.add(system)
            db.session.commit()
            return RestProtocol(system)


''' class ParentSystemFindOperationBookListApi(Resource):
    def __init__(self):
        super(ParentSystemFindOperationBookListApi, self).__init__()

    def get(self, **kwargs):
        system = TradeSystem.find(**kwargs)
        if system:
            if system.parent_sys_id == None:
                sys_list = [system]
                for child_sys in system.child_systems:
                    sys_list.append(child_sys)
                ob_list = []
                for sys in sys_list:
                    for ob in sys.operation_book:
                        ob_list.append(ob)
                return RestProtocol(ob_list)
            else:
                return RestProtocol(DataNotMatchError('The system is not a parent system.'))
        else:
            return {'message': 'System not found.'}, 404 '''


class SystemFindOperationBookApi(Resource):
    def __init__(self):
        super(SystemFindOperationBookApi, self).__init__()
        self.op_book_groups = {}
        self.system_list = []

    def find_systems(self, sys):
        self.system_list.append(sys.id)
        for child_sys in sys.child_systems:
            self.find_systems(child_sys)

    def find_operation_books(self):
        op_books = OperationBook.query.filter(
            OperationBook.sys_id.in_(self.system_list),
            OperationBook.disabled == False
        ).order_by(OperationBook.order).all()
        for ob in op_books:
            record = self.find_op_record(ob)
            if ob.catalog not in self.op_book_groups:
                self.op_book_groups[ob.catalog] = {
                    'name': ob.catalog.name,
                    'details': []
                }
            dtl = {
                'id': ob.id,
                'op_name': ob.name,
                'op_desc': ob.description,
                'type': str(ob.type).split('.')[1],
                'catalog_id': ob.catalog.id,
                'sys_id': ob.sys_id,
                'disabled': ob.disabled,
                'connection': ob.detail['remote']['name'],
                'err_code': -1,
                'interactivator': {
                    'isTrue': ob.type.IsInteractivator()
                }
            }
            if record:
                dtl['his_results'] = {
                    'err_code': record.results[-1].error_code,
                    'operated_at': record.operated_at.humanize(),
                    'operator': record.operator.name,
                    'lines': record.results[-1].detail or []
                }
            self.op_book_groups[ob.catalog]['details'].append(dtl)

    def find_op_record(self, op):
        record = EmergeOpRecord.query \
            .filter(EmergeOpRecord.emergeop_id == op.id) \
            .order_by(EmergeOpRecord.operated_at.desc()).first()
        return record

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_systems(sys)
            self.find_operation_books()
            res = [self.op_book_groups[key] for key in sorted(
                self.op_book_groups.keys(), key=lambda key: key.order
            )]
            return RestProtocol(res)
        else:
            return RestProtocol(message='System not found.', error_code=-1), 404


class SystemSystemListInformationApi(Resource):
    def __init__(self):
        super(SystemSystemListInformationApi, self).__init__()
        self.systems = []

    def get(self, **kwargs):
        parent_sys = TradeSystem.find(**kwargs)
        if parent_sys:
            if parent_sys.parent_sys_id == None:
                self.systems.append(parent_sys)
                self.find_systems(parent_sys)
                return RestProtocol(self.systems)
            else:
                return RestProtocol(DataNotMatchError('The system is not a parent system.'))
        else:
            return {'message': 'System not found.'}, 404

    def find_systems(self, parent_sys):
        for child_sys in parent_sys.child_systems:
            if child_sys.disabled is False:
                self.systems.append(child_sys)
                if child_sys.child_systems:
                    self.find_systems(child_sys)


class SystemTreeStructureApi(Resource):
    def __init__(self):
        super(SystemTreeStructureApi, self).__init__()
        self.trees = []

    def get(self):
        par_sys = TradeSystem.query.filter(TradeSystem.parent_sys_id == None).filter(
            TradeSystem.disabled == False).all()
        for sys in par_sys:
            data = dict(id=sys.id,
                        name=sys.name,
                        ip=sys.ip,
                        child=[],
                        parent_id=sys.parent_system.id if sys.parent_system else None)
            self.trees.append(data)
        self.generate_tree(par_sys, self.trees)
        return self.trees

    def generate_tree(self, obj, obj_list):
        for i, par in enumerate(obj):
            for sys in par.child_systems:
                if sys.disabled is False:
                    data = dict(id=sys.id,
                                name=sys.name,
                                ip=sys.ip,
                                child=[],
                                parent_id=sys.parent_system.id if sys.parent_system else None)
                    obj_list[i]['child'].append(data)
                    if sys.child_systems:
                        self.generate_tree(par.child_systems, obj_list[i]['child'])
