from . import db
from sqlalchemy_utils.types import ChoiceType, JSONType, IPAddressType, ArrowType
from flask_login import UserMixin
from neomodel import (StructuredNode, RelationshipTo, RelationshipFrom, Relationship,
                      StringProperty, DateProperty, IntegerProperty, UniqueIdProperty, BooleanProperty,
                      ZeroOrOne, One)
from .relations import *
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from ipaddress import IPv4Address
from arrow import Arrow

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

class SQLModelMixin(object):
    @classmethod
    def find(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    def to_json(self):
        fields = {}
        for field in [x for x in dir(self) 
                        if not x.startswith('_') 
                        and x != 'metadata'
                        and x != 'query'
                        and not x.startswith('password')
                     ]:
            data = getattr(self, field)
            if not callable(data):
                if isinstance(data, list):
                    fields[field] = [x.name for x in data]
                elif isinstance(data, db.Query):
                    fields[field] = [x.name for x in data.all()]
                elif isinstance(data, IPv4Address):
                    fields[field] = data.exploded
                elif isinstance(data, Arrow):
                    fields[field] = data.to('local').format('YYYY-MM-DD HH:mm:ss ZZ')
                elif hasattr(data, 'name'):
                    fields[field] = data.name
                else:
                    fields[field] = data
        return fields

operator_role = db.Table('operator_role',
    db.Column('operator_id', db.Integer, db.ForeignKey('operators.id'), index=True),
    db.Column('role_id',db.Integer, db.ForeignKey('roles.id'), index=True)
)

role_privilege = db.Table('role_privilege',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), index=True),
    db.Column('privilege_id', db.Integer, db.ForeignKey('privileges.id'), index=True)
)

operator_system = db.Table('operator_system',
    db.Column('operator_id', db.Integer, db.ForeignKey('operators.id'), index=True),
    db.Column('system_id', db.Integer, db.ForeignKey('trade_systems.id'), index=True),
)

operator_server = db.Table('operator_server',
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
    master = 1
    slave = 2

class MethodType(Enum):
    get = 1
    put = 2
    post = 4
    delete = 8
    all = get|put|post|delete

class ScriptType(Enum):
    checker = 1
    starter = 2
    stopper = 4
    cleaner = 8

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

class Status(Enum):
    Stopped = 1
    Running = 2
    Idle = 3

class Operator(UserMixin, SQLModelMixin, db.Model):
    def __init__(self, login, password, name=None):
        self.login = login
        self.password = password
        if name:
            self.name = name
        else:
            self.name = login
        super(Operator, self).__init__()

    __tablename__ = 'operators'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, index=True)
    name = db.Column(db.String, index=True)
    password_hash = db.Column(db.String, nullable=False)
    roles = db.relationship('OpRole',
        secondary=operator_role,
        backref=db.backref('users', lazy='dynamic'),
        lazy='dynamic'
    )
    managed_servers = db.relationship('Server',
        secondary=operator_server,
        backref=db.backref('administrators', lazy='dynamic'),
        lazy='dynamic'
    )
    managed_systems = db.relationship('TradeSystem',
        secondary=operator_system,
        backref=db.backref('administrators', lazy='dynamic'),
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

    def __repr__(self):
        return '<Operator %r>' % self.login

class OpRole(SQLModelMixin, db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)
    privileges = db.relationship('OpPrivilege',
        secondary=role_privilege,
        backref=db.backref('roles', lazy='dynamic'),
        lazy='dynamic'
    )

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<OpRole %r>' % self.name

class OpPrivilege(SQLModelMixin, db.Model):
    __tablename__ = 'privileges'
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.String, nullable=False, index=True)
    bit = db.Column(ChoiceType(MethodType, impl=db.Integer()))

class TradeProcess(SQLModelMixin, db.Model):
    def __init__(self, name, sys_id, svr_id, type=HaType.master):
        self.name = name
        self.sys_id = sys_id
        self.svr_id = svr_id
        self.type = type
        super(TradeProcess, self).__init__()

    __tablename__ = 'trade_processes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True)
    description = db.Column(db.String)
    type = db.Column(ChoiceType(HaType, impl=db.Integer()))
    base_dir = db.Column(db.String)
    exec_file = db.Column(db.String)
    sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'), index=True)
    svr_id = db.Column(db.Integer, db.ForeignKey('servers.id'), index=True)
    config_files = db.relationship('ConfigFile', backref='process')
    status = db.Column(ChoiceType(Status, impl=db.Integer()))

class SystemType(SQLModelMixin, db.Model):
    __tablename__ = 'system_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)
    description = db.Column(db.String)
    systems = db.relationship('TradeSystem', backref='type')

class TradeSystem(SQLModelMixin, db.Model):
    __tablename__ = 'trade_systems'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)
    description = db.Column(db.String)
    type_id = db.Column(db.Integer, db.ForeignKey('system_types.id'), index=True)
    version = db.Column(db.String)
    manage_ip = db.Column(IPAddressType, index=True)
    login_user = db.Column(db.String, index=True)
    login_pwd = db.Column(db.String)
    base_dir = db.Column(db.String)
    processes = db.relationship('TradeProcess', backref='system')
    servers = db.relationship('Server',
        secondary='trade_processes',
        backref=db.backref('systems', lazy='dynamic'),
        lazy='dynamic'
    )
    config_files = db.relationship('ConfigFile', backref='system')
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), index=True)
    parent_sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'), index=True)
    parent_system = db.relationship('TradeSystem', backref='child_systems', remote_side=[id])
    status = db.Column(ChoiceType(Status, impl=db.Integer()))
    
    @property
    def up_systems(self):
        return TradeSystem.query.join(SystemDependece,  SystemDependece.up_sys_id==TradeSystem.id)\
            .filter(SystemDependece.down_sys_id==self.id).all()
    
    @property
    def down_systems(self):
        return TradeSystem.query.join(SystemDependece, SystemDependece.down_sys_id==TradeSystem.id)\
            .filter(SystemDependece.up_sys_id==self.id).all()
    
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
                
        

class SystemVendor(SQLModelMixin, db.Model):
    __tablename__ = "vendors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)
    description = db.Column(db.String)
    contactors = db.Column(JSONType)
    systems = db.relationship('TradeSystem', backref='vendor')

class Server(SQLModelMixin, db.Model):
    __tablename__ = 'servers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)
    survey = db.Column(JSONType)
    description = db.Column(db.String)
    platform = db.Column(ChoiceType(PlatformType, impl=db.Integer()))
    manage_ip = db.Column(IPAddressType, index=True)
    admin_user = db.Column(db.String, index=True)
    admin_pwd = db.Column(db.String)
    processes = db.relationship('TradeProcess', backref='server')
    statics_records = db.relationship('StaticsRecord', backref='server')

class Operation(SQLModelMixin, db.Model):
    __tablename__ = 'operations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)
    sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'), index=True)
    type = db.Column(ChoiceType(ScriptType, impl=db.Integer()))
    earliest = db.Column(ArrowType)
    latest = db.Column(ArrowType)
    detail = db.Column(JSONType, nullable=False)
    records = db.relationship('OperateRecord', backref='operation')

class OperateRecord(SQLModelMixin, db.Model):
    __tablename__ = 'operate_records'
    id = db.Column(db.Integer, primary_key=True)
    sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'), index=True)
    operation_id = db.Column(db.Integer, db.ForeignKey('operations.id'), index=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id'), index=True)
    operated_at = db.Column(ArrowType, index=True)
    authorizor_id = db.Column(db.Integer, db.ForeignKey('operators.id'), index=True)
    authorized_at = db.Column(ArrowType, index=True)
    results = db.relationship('OperateResult', backref='record')

class OperateResult(SQLModelMixin, db.Model):
    __tablename__ = 'operate_results'
    id = db.Column(db.Integer, primary_key=True)
    op_id = db.Column(db.Integer, db.ForeignKey('operate_records.id'), index=True)
    succeed = db.Column(db.Boolean)
    error_code = db.Column(db.Integer, default=0)
    detail = db.Column(JSONType, nullable=False)

class StaticsRecord(SQLModelMixin, db.Model):
    __tablename__ = 'statics_records'
    id = db.Column(db.Integer, primary_key=True)
    svr_id = db.Column(db.Integer, db.ForeignKey('servers.id'), index=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id'), index=True)
    operated_at = db.Column(ArrowType, index=True)
    type = db.Column(ChoiceType(StaticsType, impl=db.Integer()))
    detail = db.Column(JSONType, nullable=False)

class ConfigFile(SQLModelMixin, db.Model):
    __tablename__ = 'config_files'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'), index=True)
    proc_id = db.Column(db.Integer, db.ForeignKey('trade_processes.id'), index=True)
    dir = db.Column(db.String, nullable=False)
    file = db.Column(db.String, nullable=False)
    hash_code = db.Column(db.String)
    storage = db.Column(db.String)
    timestamp = db.Column(ArrowType, index=True)
    active = db.Column(db.Boolean)
