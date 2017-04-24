# -*- coding: UTF-8 -*-
from flask_restful import Resource, reqparse, request
from app.models import Server

class DeviceApi(Resource):
    def get(self, **kwargs):
        '''
        try:
            dev = Device.nodes.get(name=dev_name)
            return {"name": dev.name, "status": dev.status}
        except Device.DoesNotExist:
            return {'error': 'device not found'}, 404
        '''
        dev = Server.find(**kwargs)
        if dev:
            return {
                "message": 'server({}) found succeefully.'.format(dev.name.encode('utf-8')),
                "data": dev.to_json()
            }
        else:
            return {'message': 'server not found'}, 404
    '''
    def put(self, **kwargs):
        try:
            dev = Device.nodes.get(name=dev_name)
            dev.name = request.form['dev_name']
            dev.save()
            return {"name": dev.name, "status": dev.status}
        except Device.DoesNotExist:
            return {'error': 'device not found'}, 404
        dev = Server.find(**kwargs)
        if dev:
            dev.name = request.form['dev_name']
            return {"message": 'server({}) found succeefully.'.format(dev.name), "data": dev.to_json()}
        else:
            return {'message': 'server not found'}, 404
    '''

class DeviceListApi(Resource):
    def get(self):
        devices = Server.query.all()
        '''
        for dev in Device.nodes.filter():
            devices['records'].append({"uuid": dev.uuid, "name": dev.name, "status": dev.status})
        '''
        if devices:
            return {
                'message': 'all servers listed.',
                'data': {
                    'count': len(devices),
                    'records': [
                        dev.to_json() for dev in devices
                    ]
                }
            }
        else:
            return {
                'message': 'no servers.'
            }, 204
    def post(self):
        pass
