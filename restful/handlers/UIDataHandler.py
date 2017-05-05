# -*- coding: UTF-8 -*-
from os import path
from sys import argv
from app.models import Server, TradeSystem
from flask import url_for, request, redirect
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
            system = {
                'id': sys.id,
                'icon': 'am-icon-table',
                'name': sys.name,
                'desc': sys.description,
                'isSecond': len(sys.operation_groups) > 0,
                'isShow': False,
                'Url': '#statics/{}'.format(sys.id),
                'secondName': [
                    {
                        'id': group.id,
                        'name': group.name,
                        'Url': '#op_group/{}'.format(group.id)
                    } for group in sys.operation_groups]
            }
            rtn.append(system)
        return rtn

    def map(self):
        try:
            name = request.values['name']
        except KeyError:
            return {
                'message': 'no name specified.'
            }, 404
        uri = url_for('static', filename='json/map/{}.json'.format(name))
        base_path = path.dirname(argv[0])
        abs_path = path.join(base_path, 'app{}'.format(uri))
        if path.isfile(abs_path):
            return redirect(uri)
        else:
            return {
                'message': 'no map data for {}.'.format(name)
            }, 404

    def idc(self):
        return [
            {'name': '上海', 'value': [121.48, 31.22, 20]},
            {'name': '大连', 'value': [121.46, 39.03, 15]},
            {'name': '郑州', 'value': [113.65, 34.76, 10]},
        ]
