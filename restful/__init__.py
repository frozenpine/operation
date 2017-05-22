from flask import Blueprint
from flask_restful import Api
from flask_login import login_required

restapi = Blueprint('api', __name__)
resources = Api(restapi, decorators=[login_required])
#resources = Api(restapi)

from . import uris
