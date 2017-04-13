# -*- coding: UTF-8 -*-
from app import task_queue
from flask_restful import Resource, reqparse, request
from app.models import OperationGroup, Operation, OperateRecord, OperateResult

class TaskApi(Resource):
    def get(self, **kwargs):
        pass
