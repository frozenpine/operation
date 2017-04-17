# -*- coding: UTF-8 -*-
from flask_restful import Resource, request

class LogApi(Resource):
    def post(self):
        msg = request.form['msg']
        #logging.debug(msg)
        print msg
