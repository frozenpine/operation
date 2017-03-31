# -*- coding: UTF-8 -*-
from app.models import Server, TradeSystem
from flask import url_for
from flask_restful import Resource

class SideBar(Resource):
    def get(self):
        devices = Server.query.all()
        systems = TradeSystem.query.all()
        list = []
        list.append(
            {
                "id":"1",
                "icon": "am-icon-cog",
                "isSecond": 'true',
                "name": u"设备信息",
                "Url": "javascript:;",
                "secondName": [
                    {
                        "name": dev.name,
                        "url": url_for('api.deviceapi', dev_name=dev.name)
                    } for dev in devices]
            })
        list.append(
            {
                "id":"2",
                "icon": "am-icon-server",
                "isSecond": 'true',
                "name": u"系统信息",
                "Url": "javascript:;",
                "secondName": [
                    {
                        "name": sys.name,
                        "url": "#temp{0}".format(sys.id)
                    } for sys in systems]
            })
        list.append(
            {
                "id":"3",
                "icon": "am-icon-table",
                "isSecond": 'true',
                "name": u"任务列表",
                "Url": "#temp3",
            })
        list.append(
            {
                "id":"4",
                "icon": "am-icon-bolt",
                "isSecond": 'false',
                "name": u"告警信息",
                "Url": "#temp4"
            })
        return list