from . import app, login_manager
from neomodel import (db, config, 
                      StructuredNode, RelationshipTo, RelationshipFrom, Relationship,
                      StringProperty, DateProperty, IntegerProperty, UniqueIdProperty, BooleanProperty,
                      ZeroOrOne, One)
from .relations import *
from workflow.models import Token
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

config.DATABASE_URL = 'bolt://neo4j:022010144blue@192.168.101.152:7687'
config.FORCE_TIMEZONE = True

class User(Token, UserMixin):
    SEX = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    login = StringProperty(required=True, unique_index=True)
    @classmethod
    def find_user(cls, **kwargs):
        try:
            if "login" in kwargs:
                return User.nodes.get(login=kwargs['login'], disabled=False)
        except User.DoesNotExist:
            return None

    password_hash = StringProperty(required=True)
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    sex = StringProperty(choices=SEX)
    age = IntegerProperty()
    birth = DateProperty()
    disabled = BooleanProperty(default=False)
    groups = RelationshipTo('UserGroup', 'CONTAINED')
    roles = RelationshipTo('Role', 'CONTAINED')
    managed_devices = RelationshipTo('Device', 'MANAGED', model=Authorization)
    managed_systems = RelationshipTo('System', 'MANAGED', model=Authorization)

class Device(Token):
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

class Interface(Token):
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

class System(Token):
    device = RelationshipTo('Device', 'DEPENDED', cardinality="One")
    depend_systems = RelationshipTo('System', 'DEPENDED')
    version = StringProperty()
    administrations = RelationshipFrom('User', 'MANAGED', model=Authorization)

class Manufactory(Token):
    productions = RelationshipFrom('Device', 'PRODUCED')

class Vender(Token):
    supplies = RelationshipFrom('Device', 'SUPPLIED')

class UserGroup(Token):
    users = RelationshipFrom('User', 'CONTAINED')
    roles = RelationshipTo('Role', 'CONTAINED')
    parents = RelationshipTo('UserGroup', 'CONTAINED')
    children = RelationshipFrom('UserGroup', 'CONTAINED')

class Role(Token):
    users = RelationshipFrom('User', 'CONTAINED')
    groups = RelationshipFrom('UserGroup', 'CONTAINED')
    parents = RelationshipTo('Role', 'CONTAINED')
    children = RelationshipFrom('Role', 'CONTAINED')
    privileges = RelationshipTo('Privilege', 'AUTHORIZED', model=Authorization)

class Privilege(Token):
    level = IntegerProperty(default=1)

