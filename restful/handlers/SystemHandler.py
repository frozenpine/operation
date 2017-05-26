# -*- coding: UTF-8 -*-
from flask_restful import Resource, reqparse, request
from app.models import TradeSystem

class SystemApi(Resource):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            return {
                "message": 'system({}) found succeefully.'.format(sys.name.encode('utf-8')),
                "data": sys.to_json()
            }
        else:
            return {'message': 'system not found'}, 404

    def put(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            pass
        else:
            return {'message': 'system not found'}, 404

class SystemListApi(Resource):
    def get(self):
        systems = TradeSystem.query.filter(TradeSystem.parent_sys_id==None).all()
        if systems:
            return {
                'message': 'all systems listed.',
                'data': {
                    'count': len(systems),
                    'records': [
                        sys.to_json() for sys in systems
                    ]
                }
            }
        else:
            return {
                'message': 'no systems.'
            }, 204
