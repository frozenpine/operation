# -*- coding: UTF-8 -*-
from flask_restful import Resource, request
from app import msgQueues

class LogApi(Resource):
    def post(self):
        msg = request.values['msg']
        #source = request.headers.get('src')
        #topic = request.headers.get('topic')
        #print msg, source
        '''
        if topic:
            print topic
            msgQueues[topic].put_message(msg)
        else:
        '''
        msgQueues['public'].send_message(msg.encode('utf-8'))
