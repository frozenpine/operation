from neomodel import StructuredRel, RelationshipFrom, \
StringProperty, IntegerProperty, DateProperty, DateTimeProperty

class Authorized(StructuredRel):
    authorized_time = DateTimeProperty(default_now=True)
    authorized_by = StringProperty(required=True)

class ConnWithDatetime(StructuredRel):
    since = DateTimeProperty(default_now=True)
