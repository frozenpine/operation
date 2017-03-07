from app import app
from neomodel import config, db, \
StructuredNode, RelationshipTo, RelationshipFrom, \
StringProperty, IntegerProperty, UniqueIdProperty, DateProperty

config.DATABASE_URL = app.config['NEO4J_DATABASE_URI']

from relations import *

class User(StructuredNode):
    SEXES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('Mid', 'Middle')
    )
    uid = UniqueIdProperty()
    name = StringProperty()
    login_name = StringProperty(unique_index=True)
    age = IntegerProperty()
    sex = StringProperty(required=True, choices=SEXES)
    password = StringProperty()
    created_time = DateTimeProperty(default_now=True)
    title = StringProperty()
    manage_device = RelationshipTo('Device', 'MANAGE', model=Authorized)

class Device(StructuredNode):
    STATUS = (
        ('PRD', 'In Production Environment.'),
        ('SIM', 'In Simulation Environment.'),
        ('TST', 'In Testing Environment.'),
        ('')
    )
    uid = UniqueIdProperty()
    name = StringProperty(required=True, unique_index=True)
    model = StringProperty()
    serial_num = StringProperty()
    vender = RelationshipFrom('Vender', 'SUPPLY', model=ConnWithDatetime)
    manufactory = RelationshipFrom('Manufactory', 'PRODUCE', model=ConnWithDatetime)
    purchase_date = DateProperty()
    warranty = IntegerProperty(default=1)
    status = StringProperty(required=True, choices=STATUS)
    administrator = RelationshipFrom('User', 'MANAGE', model=Authorized)

class Manufactory(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(required=True, unique_index=True)
    description = StringProperty()
    productions = RelationshipTo('Device', 'PRODUCE', model=ConnWithDatetime)

class Vender(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(required=True, unique_index=True)
    description = StringProperty()
    supplies = RelationshipTo('Device', 'SUPPLY', model=ConnWithDatetime)
