# -*- coding: UTF-8 -*-
from flask_restful import Resource, reqparse, request
from app.models import TradeSystem

class OperationListApi(Resource):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        return {
            'target': sys.to_json(),
            'operations': [x for x in range(1, 10)],
            'method': request.method
        }
