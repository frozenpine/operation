from app import app
from flask_restful import Api
from restful.resources.UserHandler import UserApi, UserListApi
from restful.resources.DeviceHandler import DeviceApi, DeviceListApi

uri = Api(app)

uri.add_resource(UserApi, '/api/users/<string:login>', endpoint='user')
uri.add_resource(UserListApi, '/api/users', '/api/users/', endpoint='users')

uri.add_resource(DeviceApi, '/api/devices/<string:dev_name>', endpoint='device')
uri.add_resource(DeviceListApi, '/api/devices', '/api/devices/', endpoint='devices')
