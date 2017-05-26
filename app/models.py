# -*- coding: UTF-8 -*-
from . import db
from sqlalchemy_utils.types import (
    ChoiceType, JSONType, IPAddressType, ArrowType,
    DateTimeRangeType
)
from sqlalchemy_utils import observes
from flask_login import UserMixin
'''
from neomodel import (
    StructuredNode, RelationshipTo, RelationshipFrom, Relationship,
    StringProperty, DateProperty, IntegerProperty, UniqueIdProperty, BooleanProperty,
    ZeroOrOne, One
)
from .relations import *
'''
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from ipaddress import IPv4Address
from arrow import Arrow
import re
import json
from uuid import uuid4
from datetime import time, datetime

'''
class NodeMixin(StructuredNode):
    __abstract_node__ = True
    uuid = UniqueIdProperty()
    name = StringProperty(required=True, index=True)
    description = StringProperty()
    created_time = DateTimeProperty(default_now=True)
    disabled = BooleanProperty(default=False)

    @classmethod
    def find(cls, **kwargs):
        try:
            return cls.nodes.get(**kwargs)
        except cls.DoesNotExist:
            return None

class User(NodeMixin, UserMixin):
    SEX = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    login = StringProperty(required=True, unique_index=True)

    password_hash = StringProperty(required=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    def get_id(self):
        return self.uuid

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    sex = StringProperty(choices=SEX)
    age = IntegerProperty()
    birth = DateProperty()
    groups = RelationshipTo('UserGroup', 'CONTAINED')
    roles = RelationshipTo('Role', 'CONTAINED')
    managed_devices = RelationshipTo('Device', 'MANAGED', model=Authorization)
    managed_systems = RelationshipTo('System', 'MANAGED', model=Authorization)

class Device(NodeMixin):
    STATUS = (
        ('PRD', 'In Production Environment.'),
        ('SIM', 'In Simulation Environment.'),
        ('TST', 'In Testing Environment.'),
        ('STO', 'Stored in warehouse.'),
        ('JUK', 'Scrapped on overworking')
    )
    model = StringProperty()
    serial_num = StringProperty()
    vender = RelationshipTo('Vender', 'SUPPLIED')
    manufactory = RelationshipTo('Manufactory', 'PRODUCED')
    purchase_date = DateProperty()
    warranty = IntegerProperty(default=12, help_text="Warranty count in month, default=12")
    status = StringProperty(required=True, choices=STATUS)
    systems = RelationshipFrom('System', 'DEPENDED', cardinality=ZeroOrOne)
    interfaces = RelationshipFrom('Interface', 'CONTAINED')
    administrations = RelationshipFrom('User', 'MANAGED', model=Authorization)

class Interface(NodeMixin):
    STATUS = (
        ('UP', 'Interface UP'),
        ('DOWN', 'Interface Down'),
        ('INVAID', 'Interface Invalid')
    )
    status = StringProperty(choices=STATUS, default='DOWN')
    connection = Relationship('Interface', 'CONNECTED', model=Connection, cardinality=ZeroOrOne)
    device = RelationshipTo('Device',  'CONTAINED', cardinality=One)
    model = StringProperty()
    speed = IntegerProperty(default=1000)

class System(NodeMixin):
    device = RelationshipTo('Device', 'DEPENDED', cardinality="One")
    depend_systems = RelationshipTo('System', 'DEPENDED')
    version = StringProperty()
    administrations = RelationshipFrom('User', 'MANAGED', model=Authorization)

class Manufactory(NodeMixin):
    productions = RelationshipFrom('Device', 'PRODUCED')

class Vender(NodeMixin):
    supplies = RelationshipFrom('Device', 'SUPPLIED')

class UserGroup(NodeMixin):
    users = RelationshipFrom('User', 'CONTAINED')
    roles = RelationshipTo('Role', 'CONTAINED')
    parents = RelationshipTo('UserGroup', 'CONTAINED')
    children = RelationshipFrom('UserGroup', 'CONTAINED')

class Role(NodeMixin):
    users = RelationshipFrom('User', 'CONTAINED')
    groups = RelationshipFrom('UserGroup', 'CONTAINED')
    parents = RelationshipTo('Role', 'CONTAINED')
    children = RelationshipFrom('Role', 'CONTAINED')
    privileges = RelationshipTo('Privilege', 'AUTHORIZED', model=Authorization)

class Privilege(NodeMixin):
    level = IntegerProperty(default=1)
'''

class SQLModelMixin(object):
    filter_keyword = [
        'is_active',
        'is_anonymous',
        'is_authenticated',
        'metadata',
        'query',
        'filter_keyword',
        'level'
    ]
    level = 0

    @classmethod
    def find(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    def to_json(self, depth=1):
        results = {}
        for field in [x for x in dir(self) if not re.match(
            r'^_|\w*p(?:ass)?w(?:or)?d|\w+_id$', x, re.I
        ) and x not in self.filter_keyword]:
            data = getattr(self, field)
            if not callable(data):
                if isinstance(data, list) or isinstance(data, dict):
                    results[field] = json.dumps(data)
                elif isinstance(data, db.Query):
                    results[field] = [x.name for x in data.all()]
                elif isinstance(data, IPv4Address):
                    results[field] = data.exploded
                elif isinstance(data, Arrow):
                    results[field] = data.to('local').format('YYYY-MM-DD HH:mm:ss ZZ')
                elif hasattr(data, 'name'):
                    results[field] = data.name
                else:
                    results[field] = data
        return results

operator_role = db.Table(
    'operator_role',
    db.Column('operator_id', db.Integer, db.ForeignKey('operators.id'), index=True),
    db.Column('role_id',db.Integer, db.ForeignKey('roles.id'), index=True)
)

role_privilege = db.Table(
    'role_privilege',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), index=True),
    db.Column('privilege_id', db.Integer, db.ForeignKey('privileges.id'), index=True)
)

operator_system = db.Table(
    'operator_system',
    db.Column('operator_id', db.Integer, db.ForeignKey('operators.id'), index=True),
    db.Column('system_id', db.Integer, db.ForeignKey('trade_systems.id'), index=True),
)

operator_server = db.Table(
    'operator_server',
    db.Column('operator_id', db.Integer, db.ForeignKey('operators.id'), index=True),
    db.Column('system_id', db.Integer, db.ForeignKey('servers.id'), index=True),
)

class SystemDependece(db.Model):
    __tablename__ = 'system_system'
    up_sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'), primary_key=True)
    down_sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'), primary_key=True)

    def __init__(self, up_sys_id, down_sys_id):
        self.up_sys_id = up_sys_id
        self.down_sys_id = down_sys_id

class HaType(Enum):
    Master = 1
    Slave = 2

class MethodType(Enum):
    Get = 1
    Put = 2
    Post = 4
    Delete = 8
    Get_Post = Get|Post
    Get_Put = Get|Put
    Get_Delete = Get|Delete
    Put_Post = Put|Post
    Put_Delete = Put|Delete
    Post_Delete = Post|Delete
    Get_Put_Post = Get_Put|Post
    Get_Put_Delete = Get_Put|Delete
    Get_Post_Delete = Get_Post|Delete
    Put_Post_Delete = Put_Post|Delete
    All = Get|Put|Post|Delete

class DataSourceType(Enum):
    SQL = 1
    FILE = 2

class DataSourceModel(Enum):
    Seat = 1
    Session = 2

class ScriptType(Enum):
    Checker = 1
    Executor = 2
    Interactivator = 4
    Excute_Checker = Executor|Checker
    Interactive_Checker = Interactivator|Checker

    def IsBatcher(self):
        return self.value & ScriptType.Excute_Checker.value \
            == ScriptType.Excute_Checker.value or \
            self.value & ScriptType.Interactive_Checker.value \
            == ScriptType.Interactive_Checker.value

    def IsChecker(self):
        return self.value & ScriptType.Checker.value \
            == ScriptType.Checker.value

    def IsInteractivator(self):
        return self.value & ScriptType.Interactivator.value \
            == ScriptType.Interactivator.value

class PlatformType(Enum):
    Linux = 1
    Windows = 2
    Unix = 3
    BSD = 4
    Embedded = 5

class StaticsType(Enum):
    CPU = 1
    MOUNT = 2
    DISK = 3
    MEMORY = 4
    SWAP = 5
    NETWORK = 6

class OperateRecord(SQLModelMixin, db.Model):
    __tablename__ = 'operate_records'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.id'), index=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id'), index=True)
    operated_at = db.Column(ArrowType, index=True)
    authorizor_id = db.Column(db.Integer, db.ForeignKey('operators.id'), index=True)
    authorized_at = db.Column(ArrowType, index=True)
    results = db.relationship('OperateResult', backref='record')

class Operator(UserMixin, SQLModelMixin, db.Model):
    def __init__(self, login, password, name=None, **kwargs):
        self.login = login
        self.password = password
        if name:
            self.name = name
        else:
            self.name = login
        super(Operator, self).__init__(**kwargs)

    __tablename__ = 'operators'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String, unique=True, index=True)
    name = db.Column(db.String, index=True)
    password_hash = db.Column(db.String, nullable=False)
    roles = db.relationship(
        'OpRole',
        secondary=operator_role,
        backref=db.backref('users', lazy='dynamic'),
        lazy='dynamic'
    )
    managed_servers = db.relationship(
        'Server',
        secondary=operator_server,
        backref=db.backref('administrators', lazy='dynamic'),
        lazy='dynamic'
    )
    managed_systems = db.relationship(
        'TradeSystem',
        secondary=operator_system,
        backref=db.backref('administrators', lazy='dynamic'),
        lazy='dynamic'
    )
    operation_records = db.relationship(
        'OperateRecord',
        backref='operator',
        foreign_keys=[OperateRecord.operator_id],
        lazy='dynamic'
    )
    authorization_records = db.relationship(
        'OperateRecord',
        backref='authorizor',
        foreign_keys=[OperateRecord.authorizor_id],
        lazy='dynamic'
    )

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class OpRole(SQLModelMixin, db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, index=True)
    privileges = db.relationship(
        'OpPrivilege',
        secondary=role_privilege,
        backref=db.backref('roles', lazy='dynamic'),
        lazy='dynamic'
    )

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<OpRole {}>'.format(self.name)

class OpPrivilege(SQLModelMixin, db.Model):
    __tablename__ = 'privileges'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    @property
    def name(self):
        return '{}.{}'.format(self.uri, self.bit.name)
    uri = db.Column(db.String, nullable=False, index=True)
    bit = db.Column(ChoiceType(MethodType, impl=db.Integer()))

class TradeProcess(SQLModelMixin, db.Model):
    def __init__(self, name, sys_id, svr_id, type=HaType.Master, **kwargs):
        self.name = name
        self.sys_id = sys_id
        self.svr_id = svr_id
        self.type = type
        super(TradeProcess, self).__init__(**kwargs)

    __tablename__ = 'trade_processes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(
        db.String, index=True,
        default=lambda: unicode(uuid4()).lower()
    )
    name = db.Column(db.String, nullable=False, index=True)
    description = db.Column(db.String)
    type = db.Column(ChoiceType(HaType, impl=db.Integer()), default=HaType.Master)
    base_dir = db.Column(db.String)
    exec_file = db.Column(db.String, nullable=False)
    param = db.Column(db.String)
    sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'), index=True)
    svr_id = db.Column(db.Integer, db.ForeignKey('servers.id'), index=True)
    config_files = db.relationship('ConfigFile', backref='process', lazy='dynamic')
    status = db.Column(JSONType, default={})

class SystemType(SQLModelMixin, db.Model):
    __tablename__ = 'system_types'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, index=True)
    description = db.Column(db.String)
    systems = db.relationship('TradeSystem', backref='type', lazy='dynamic')

class TradeSystem(SQLModelMixin, db.Model):
    __tablename__ = 'trade_systems'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(
        db.String, index=True,
        default=lambda: unicode(uuid4()).lower()
    )
    name = db.Column(db.String, unique=True, index=True)
    description = db.Column(db.String)
    type_id = db.Column(db.Integer, db.ForeignKey('system_types.id'), index=True)
    version = db.Column(db.String)
    manage_ip = db.Column(IPAddressType, index=True)
    login_user = db.Column(db.String, index=True)
    login_pwd = db.Column(db.String)
    base_dir = db.Column(db.String)
    processes = db.relationship('TradeProcess', backref='system')
    servers = db.relationship(
        'Server',
        secondary='trade_processes',
        backref=db.backref('systems', lazy='dynamic'),
        lazy='dynamic'
    )
    config_files = db.relationship('ConfigFile', backref='system', lazy='dynamic')
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), index=True)
    parent_sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'), index=True)
    parent_system = db.relationship('TradeSystem', backref='child_systems', remote_side=[id])
    operation_groups = db.relationship('OperationGroup', backref='system')
    operations = db.relationship('Operation', backref='system', lazy='dynamic')
    data_sources = db.relationship('DataSource', backref='system', lazy='dynamic')

    @property
    def up_systems(self):
        return TradeSystem.query.join(
            SystemDependece,
            SystemDependece.up_sys_id == TradeSystem.id
        ).filter(
            SystemDependece.down_sys_id == self.id
        ).all()

    @property
    def down_systems(self):
        return TradeSystem.query.join(
            SystemDependece,
            SystemDependece.down_sys_id == TradeSystem.id
        ).filter(
            SystemDependece.up_sys_id == self.id
        ).all()

    def AddDependence(self, up_sys):
        if isinstance(up_sys, TradeSystem):
            if self.id is not None and up_sys.id is not None:
                db.session.add(SystemDependece(up_sys.id, self.id))
                db.session.commit()
            else:
                db.session.add_all([self, up_sys])
                db.session.commit()
                db.session.add(SystemDependece(up_sys.id, self.id))
                db.session.commit()
        else:
            raise TypeError('{} is not <class:{}>'.format(up_sys, self.__name__))

class DataSource(SQLModelMixin, db.Model):
    __tablename__ = "data_sources"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, index=True)
    description = db.Column(db.String)
    sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'), index=True)
    src_type = db.Column(
        ChoiceType(DataSourceType, impl=db.Integer()),
        default=DataSourceType.SQL,
        nullable=False
    )
    src_model = db.Column(ChoiceType(DataSourceModel, impl=db.Integer()), nullable=False)
    source = db.Column(JSONType, nullable=False)

class SystemVendor(SQLModelMixin, db.Model):
    __tablename__ = "vendors"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, index=True)
    description = db.Column(db.String)
    contactors = db.Column(JSONType, default={})
    systems = db.relationship('TradeSystem', backref='vendor', lazy='dynamic')

class Server(SQLModelMixin, db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(
        db.String, index=True,
        default=lambda: unicode(uuid4()).lower()
    )
    name = db.Column(db.String, unique=True, index=True)
    survey = db.Column(JSONType, default={})
    description = db.Column(db.String)
    platform = db.Column(ChoiceType(PlatformType, impl=db.Integer()), default=PlatformType.Linux)
    manage_ip = db.Column(IPAddressType, index=True)
    admin_user = db.Column(db.String, index=True)
    admin_pwd = db.Column(db.String)
    processes = db.relationship('TradeProcess', backref='server', lazy='dynamic')
    statics_records = db.relationship('StaticsRecord', backref='server', lazy='dynamic')
    status = db.Column(JSONType, default={})

class Operation(SQLModelMixin, db.Model):
    __tablename__ = 'operations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, index=True)
    description = db.Column(db.String)
    type = db.Column(ChoiceType(ScriptType, impl=db.Integer()))
    earliest = db.Column(db.String)
    latest = db.Column(db.String)
    @property
    def time_range(self):
        early_hour, early_minute = (None, None)
        if self.earliest:
            early_hour, early_minute = self.earliest.split(':')
        late_hour, late_minute = (None, None)
        if self.latest:
            late_hour, late_minute = self.latest.split(':')
        if early_hour and late_hour:
            return time(int(early_hour), int(early_minute)), time(int(late_hour), int(late_minute))
        elif early_hour:
            return time(int(early_hour), int(early_minute)), None
        elif late_hour:
            return None, time(int(late_hour), int(late_minute))
        else:
            return None, None

    def InTimeRange(self):
        now = datetime.now().time()
        lower, upper = self.time_range
        if lower and upper:
            return lower <= now and now <= upper
        elif lower:
            return lower <= now
        elif upper:
            return now <= upper
        else:
            return True

    detail = db.Column(JSONType, nullable=False, default={})
    @observes('sys_id')
    def remoteConfigObserver(self, sys_id):
        sys = TradeSystem.find(id=sys_id)
        if sys:
            params = self.detail['remote']['params']
            params['ip'] = sys.manage_ip.exploded
            if not (self.type & ScriptType.Interactivator.value
                    == ScriptType.Interactivator.value):
                params['user'] = sys.login_user
                params['password'] = sys.login_pwd
    order = db.Column(db.Integer)
    op_group_id = db.Column(db.Integer, db.ForeignKey('operation_groups.id'))
    sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'), index=True)
    records = db.relationship(
        'OperateRecord',
        backref='operation',
        order_by='OperateRecord.operated_at.desc()',
        lazy='dynamic'
    )

class OperationGroup(SQLModelMixin, db.Model):
    __tablename__ = 'operation_groups'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, index=True)
    description = db.Column(db.String)
    sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'), index=True)
    operations = db.relationship('Operation', backref='group', order_by='Operation.order')

class OperateResult(SQLModelMixin, db.Model):
    __tablename__ = 'operate_results'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    op_rec_id = db.Column(db.Integer, db.ForeignKey('operate_records.id'), index=True)
    error_code = db.Column(db.Integer, default=0)
    detail = db.Column(JSONType, nullable=False, default=[])

class StaticsRecord(SQLModelMixin, db.Model):
    __tablename__ = 'statics_records'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    svr_id = db.Column(db.Integer, db.ForeignKey('servers.id'), index=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id'), index=True)
    operated_at = db.Column(ArrowType, index=True)
    type = db.Column(ChoiceType(StaticsType, impl=db.Integer()))
    detail = db.Column(JSONType, nullable=False, default={})

class ConfigFile(SQLModelMixin, db.Model):
    __tablename__ = 'config_files'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, index=True)
    sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'), index=True)
    proc_id = db.Column(db.Integer, db.ForeignKey('trade_processes.id'), index=True)
    dir = db.Column(db.String, nullable=False)
    file = db.Column(db.String, nullable=False)
    hash_code = db.Column(db.String)
    storage = db.Column(db.String)
    timestamp = db.Column(ArrowType, index=True)
    active = db.Column(db.Boolean)
