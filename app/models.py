from app import app
from neomodel import (db, config, 
                      StructuredNode, RelationshipTo, RelationshipFrom, Relationship,
                      StringProperty, DateProperty, IntegerProperty, UniqueIdProperty)
from .relations import *
from fp_workflow.models import Token

config.DATABASE_URL = 'bolt://neo4j:022010144blue@192.168.101.152:7687'
config.FORCE_TIMEZONE = True

class User(Token):
    SEX = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    login = StringProperty(required=True, unique_index=True)
    password = StringProperty(required=True)
    sex = StringProperty(choices=SEX)
    age = IntegerProperty()
    devices = RelationshipFrom('Device', 'MANAGED', model=Authorized)

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
    administrator = RelationshipTo('User', 'MANAGED', model=Authorized)

class Manufactory(Token):
    productions = RelationshipFrom('Device', 'PRODUCED')

class Vender(Token):
    supplies = RelationshipFrom('Device', 'SUPPLIED')

