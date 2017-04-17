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
        systems = TradeSystem.query.filter(TradeSystem.parent_sys_id == None).all()
        rtn = []
        for sys in systems:
            system = {}
            system['id'] = sys.id
            system['icon'] = 'am-icon-table'
            system['name'] = sys.name
            system['isSecond'] = len(sys.operation_groups) > 0
            system['isShow'] = False
            system['Url'] = '#statics/{}'.format(sys.id)
            system['secondName'] = [
                {
                    'id': group.id,
                    'name': group.name,
                    'Url': '#op_group/{}'.format(group.id)
                } for group in sys.operation_groups
            ]
            rtn.append(system)
        return rtn
