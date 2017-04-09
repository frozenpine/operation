# -*- coding: UTF-8 -*-
from flask_restful import Resource, reqparse, request
from app.models import TradeSystem

class ServerStaticsApi(Resource):
    def get(self, **kwargs):
        return [
            {
                'server': 'testtest',
                'cpu': '15%',
                'memory': '36%',
                'swap': '0%',
                'diskName': '/',
                'disk': '13%'
            }
        ]

class SystemStaticsApi(Resource):
    def get(self, **kwargs):
        return [
            {
                'systemName': 'trade01',
                'server': 'testtest',
                'process': 'qtrade',
                'proc_role': 'master',
                'status': 'running'
            }
        ]
