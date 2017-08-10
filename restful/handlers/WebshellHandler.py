# -*- coding: UTF-8 -*-
from flask import render_template
from flask_restful import Resource

from app.models import TradeSystem


class WebshellUIApi(Resource):
    def get(self, id):
        sys = TradeSystem.find(id=id)
        if sys:
            return render_template(
                'Interactivators/webShell.html'
            )
        else:
            return {
                       'message': 'trade system not found.'
                   }, 404
