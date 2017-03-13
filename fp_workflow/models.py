from app import app
from neomodel import (db, config, 
                      StructuredNode, StructuredRel,
                      RelationshipTo, RelationshipFrom, Relationship,
                      StringProperty, DateTimeProperty, UniqueIdProperty, ArrayProperty)

config.DATABASE_URL = 'bolt://neo4j:022010144blue@192.168.101.152:7687'
config.FORCE_TIMEZONE = True

class Connection(StructuredRel):
    name = StringProperty()

class Place(StructuredNode):
    __abstract_node__ = True
    input = RelationshipFrom('Transition', 'FIRED', model=Connection)
    tokens = Relationship('Token', 'TOKEN')
    output = RelationshipTo('Transition', 'ENABLED', model=Connection)
    name = StringProperty(required=True)
    description = StringProperty()

class Transition(StructuredNode):
    __abstract_node__ = True
    input = RelationshipFrom('Place', 'ENABLED', model=Connection)
    output = RelationshipTo('Place', 'FIRED', model=Connection)
    name = StringProperty(required=True)

class Token(StructuredNode):
    __abstract_node__ = True
    uuid = UniqueIdProperty(requied=True)
    name = StringProperty(required=True, index=True)
    description = StringProperty()
    created_time = DateTimeProperty(default_now=True)
