from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, reqparse, request
from app.models import Device
import json

class DeviceApi(Resource):
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

class DeviceListApi(Resource):
    def get(self):
        devices = []
        for dev in Device.nodes.filter():
            devices.append({"name": dev.name, "administrator": [u.name for u in dev.administrator]})
        return devices
    def post(self):
        args = parser.parse_args()
        pass
