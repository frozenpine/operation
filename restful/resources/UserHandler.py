from flask_restful import Resource, reqparse, request
from app.models import User, Device
import json

parser = reqparse.RequestParser()
parser.add_argument('username', type=str, required=True, dest='user_name', help='username can not been none', action='append')


class UserByLogin(Resource):
    def get(self, login):
        try:
            user = User.nodes.get(login=login)
            return {"login": user.login, "name": user.name, "managed devices": [ d.name for d in user.devices]}
        except User.DoesNotExist:
            return {'error': 'user not found'}, 404
    def put(self, login):
        try:
            user = User.nodes.get(login=login)
            user.name = request.form['username']
            user.save()
            return {"login": user.login, "name": user.name, "managed devices": [ d.name for d in user.devices]}
        except User.DoesNotExist:
            return {'error': 'user not found'}, 404

class UserList(Resource):
    def get(self):
        users = []
        for user in User.nodes.filter():
            users.append({"login": user.login, "name": user.name})
        return users
    def post(self):
        args = parser.parse_args()
        pass

class DeviceByName(Resource):
    def get(self, dev_name):
        try:
            dev = Device.nodes.get(name=dev_name)
            return {"name": dev.name, "administrator": [u.name for u in dev.administrator]}
        except Device.DoesNotExist:
            return {'error': 'device not found'}, 404
    def put(self, dev_name):
        try:
            dev = Device.nodes.get(name=dev_name)
            dev.name = request.form['dev_name']
            dev.save()
            return {"name": dev.name, "administrator": [u.name for u in dev.administrator]}
        except Device.DoesNotExist:
            return {'error': 'device not found'}, 404

class DeviceList(Resource):
    def get(self):
        devices = []
        for dev in Device.nodes.filter():
            devices.append({"name": dev.name, "administrator": [u.name for u in dev.administrator]})
        return devices
    def post(self):
        args = parser.parse_args()
        pass
