from app import app
from neomodel import (config, StructuredNode, RelationshipTo, RelationshipFrom, Relationship,
                    StringProperty, DateProperty, IntegerProperty)
from .relations import *

config.DATABASE_URL = 'bolt://neo4j:022010144blue@192.168.101.152:7687'

class User(StructuredNode):
    SEX = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    name = StringProperty(required=True)
    login = StringProperty(required=True, unique_index=True)
    password = StringProperty(required=True)
    sex = StringProperty(choices=SEX)
    age = IntegerProperty()
    devices = RelationshipFrom('Device', 'MANAGED', model=Authorized)

class Device(StructuredNode):
    STATUS = (
        ('PRD', 'In Production Environment.'),
        ('SIM', 'In Simulation Environment.'),
        ('TST', 'In Testing Environment.'),
        ('STO', 'Stored in warehouse.'),
        ('JUK', 'Scrapped on overworking')
    )
    name = StringProperty(required=True, unique_index=True)
    model = StringProperty()
    serial_num = StringProperty()
    vender = RelationshipTo('Vender', 'SUPPLIED')
    manufactory = RelationshipTo('Manufactory', 'PRODUCED')
    purchase_date = DateProperty()
    warranty = IntegerProperty(default=12)
    status = StringProperty(required=True, choices=STATUS)
    administrator = RelationshipTo('User', 'MANAGED', model=Authorized)

class Manufactory(StructuredNode):
    name = StringProperty(required=True, unique_index=True)
    description = StringProperty()
    productions = RelationshipFrom('Device', 'PRODUCED')

class Vender(StructuredNode):
    name = StringProperty(required=True, unique_index=True)
    description = StringProperty()
    supplies = RelationshipFrom('Device', 'SUPPLIED')

