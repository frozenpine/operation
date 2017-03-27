from . import db
from flask_login import UserMixin
from neomodel import (StructuredNode, RelationshipTo, RelationshipFrom, Relationship,
                      StringProperty, DateProperty, IntegerProperty, UniqueIdProperty, BooleanProperty,
                      ZeroOrOne, One)
from .relations import *
from werkzeug.security import generate_password_hash, check_password_hash

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

class Operator(UserMixin, SQLModelMixin, db.Model):
    __tablename__ = 'operators'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, index=True)
    name = db.Column(db.String, index=True)
    password_hash = db.Column(db.String, nullable=False)

    def __init__(self, login, password, name=None):
        self.login = login
        self.password = password
        if name:
            self.name = name
        else:
            self.name = login

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    role_id = db.Column(db.Integer, db.ForeignKey('op_roles.id'))

    def __repr__(self):
        return '<Operator %r>' % self.login

class OpRole(SQLModelMixin, db.Model):
    __tablename__ = 'op_roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)
    users = db.relationship('Operator', backref='role')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<OpRole %r>' % self.name

class TradeSystem(SQLModelMixin, db.Model):
    __tablename__ = 'trade_systems'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)
    description = db.Column(db.String)
    version = db.Column(db.String)
    manage_ip = db.Column(db.String, nullable=False)
    login_user = db.Column(db.String, nullable=False)
    login_pwd = db.Column(db.String, nullable=False)
    process = db.relationship('TradeProcess', backref='system')

class TradeProcess(SQLModelMixin, db.Model):
    __tablename__ = 'trade_processes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    sys_id = db.Column(db.Integer, db.ForeignKey('trade_systems.id'))

