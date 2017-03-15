from app import app
from flask_restful import Api
from restful.resources.UserHandler import UserApi, UserListApi
from restful.resources.DeviceHandler import DeviceApi, DeviceListApi

uri = Api(app)

uri.add_resource(UserApi, '/apis/users/<string:login>', endpoint='user')
uri.add_resource(UserListApi, '/apis/users', '/api/users/', endpoint='users')

uri.add_resource(DeviceApi, '/apis/devices/<string:dev_name>', endpoint='device')
uri.add_resource(DeviceListApi, '/apis/devices', '/api/devices/', endpoint='devices')
