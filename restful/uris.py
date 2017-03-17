from . import resources
from .handlers.UserHandler import UserApi, UserListApi
from .handlers.DeviceHandler import DeviceApi, DeviceListApi

resources.add_resource(UserApi, '/users/<string:login>', methods=['GET', 'PUT'])
resources.add_resource(UserListApi, '/users', '/users/', methods=['GET', 'POST'])

resources.add_resource(DeviceApi, '/devices/<string:dev_name>', methods=['GET', 'PUT'])
resources.add_resource(DeviceListApi, '/devices', '/devices/', methods=['GET', 'POST'])
