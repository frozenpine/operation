# -*- coding: UTF-8 -*-
from flask_restful import Resource, reqparse, request

from app.models import OperateRecord, OperateResult, Operation, OperationGroup


class TaskApi(Resource):
    def get(self, **kwargs):
        pass
