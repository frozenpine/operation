# -*- coding: UTF-8 -*-
import json
import time

from flask import Response
from flask_restful import Resource, reqparse, request

from app.models import OperateRecord, OperateResult, Operation, OperationGroup


class TaskApi(Resource):
    def _jsonFlow(self):
        for i in xrange(10):
            time.sleep(5)
            yield (
                b'--frame\r\n'
                b'Content-Type: application/json\r\n\r\n'
                + json.dumps({
                    'key': i,
                    'value': time.time()
                })
                + b'\r\n'
            )

    def get(self):
        return Response(
            self._jsonFlow(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
