# -*- coding: UTF-8 -*-
from neomodel import (StructuredRel,
                      StringProperty, IntegerProperty, DateTimeProperty)

class Authorization(StructuredRel):
    authorizer = StringProperty(required=True)
    auth_time = DateTimeProperty(default_now=True)
    auth_level = IntegerProperty(required=True)
    auth_account = StringProperty(required=True)

class Connection(StructuredRel):
    local = StringProperty(required=True)
    remote = StringProperty(required=True)
