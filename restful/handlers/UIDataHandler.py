# -*- coding: UTF-8 -*-
from app.models import Server, TradeSystem
from flask import url_for
from flask_restful import Resource

class UIDataApi(Resource):
    def get(self, name):
        if hasattr(self, name):
            return getattr(self, name)()
        else:
            return {'message': 'resource not found.'}, 404
    def sideBarCtrl(self):
        systems = TradeSystem.query.filter(TradeSystem.parent_sys_id==None).all()
        list = []
        for sys in systems:
            system = {}
            system['id'] = sys.id
            system['icon'] = 'am-icon-table'
            system['name'] = sys.name
            system['isSecond'] = sys.child_systems is not None
            system['Url'] = '#statics'
            system['secondName'] = [
                {
                    'name': child.name,
                    'Url': '#system'
                } for child in sys.operation_groups
            ]
            list.append(system)
        return list
