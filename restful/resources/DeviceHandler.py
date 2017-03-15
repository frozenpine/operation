from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, reqparse, request
from app.models import Device
import json

class DeviceApi(Resource):
    def get(self, dev_name):
        try:
            dev = Device.nodes.get(name=dev_name)
            return {"name": dev.name, "status": dev.status}
        except Device.DoesNotExist:
            return {'error': 'device not found'}, 404
    def put(self, dev_name):
        try:
            dev = Device.nodes.get(name=dev_name)
            dev.name = request.form['dev_name']
            dev.save()
            return {"name": dev.name, "status": dev.status}
        except Device.DoesNotExist:
            return {'error': 'device not found'}, 404

class DeviceListApi(Resource):
    def get(self):
        devices = {"records": []}
        for dev in Device.nodes.filter():
            devices['records'].append({"uuid": dev.uuid, "name": dev.name, "status": dev.status})
        return devices
    def post(self):
        pass
