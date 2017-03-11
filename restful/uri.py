from app import app
from flask_restful import Api
from resources.UserHandler import *

uri = Api(app)

uri.add_resource(UserByLogin, '/api/users/<string:login>')
uri.add_resource(UserList, '/api/users', '/api/users/')

uri.add_resource(DeviceByName, '/api/devices/<string:dev_name>')
uri.add_resource(DeviceList, '/api/devices', '/api/devices/')
