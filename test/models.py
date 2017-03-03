from neomodel import config, StructuredNode, StringProperty, IntegerProperty, \
RelationshipTo, RelationshipFrom

config.DATABASE_URL = 'bolt://neo4j:022010144blue@192.168.101.152:7687'

class Device(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    model = StringProperty()
    admins = RelationshipFrom('Person', 'MANAGE')
    '''
    modules = RelationShipFrom(self, 'BELONG')
    os = RelationShipFrom('System', 'RUN')
    interfaces = RelationShipFrom('Interface', 'BELONG')
    '''

class Person(StructuredNode):
    SEXES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    name = StringProperty(required=True)
    sex = StringProperty(required=True, choices=SEXES)
    age = IntegerProperty()
    login = StringProperty(unique_index=True, required=True)
    password = StringProperty(required=True)
    devices = RelationshipTo('Person', 'MANAGE')
