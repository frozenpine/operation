# -*- coding: UTF-8 -*-
from flask_restful import Resource, request
from app import msgQueues

class LogApi(Resource):
    def post(self):
        msg = request.form['msg']
        msgQueues['public'].put_message(msg)
