from app import app
from neomodel import config, db, \
StructuredNode, RelationshipTo, RelationshipFrom, \
StringProperty, IntegerProperty, UniqueIdProperty, DateProperty

config.DATABASE_URL = app.config['NEO4J_DATABASE_URI']

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
    created_time = DateProperty(default_now=True)
