# -*- coding: UTF-8 -*-
from flask import Blueprint
from flask_restful import Api

restapi = Blueprint('api', __name__)
# resources = Api(restapi, decorators=[login_required])
resources = Api(restapi)

from . import uris
