from neomodel import (StructuredRel,
                      StringProperty, IntegerProperty, DateTimeProperty)

class Authorized(StructuredRel):
    authorizer = StringProperty(required=True)
    auth_time = DateTimeProperty(default_now=True)
    auth_level = IntegerProperty(required=True)
