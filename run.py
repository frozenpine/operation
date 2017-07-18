# -*- coding: UTF-8 -*-
import sys
from os import environ

import zerorpc

from gevent import monkey, joinall, spawn
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from multiprocessing import Process

from app import create_app
from TaskManager.controller import Controller
from TaskManager.worker import Worker


host = environ.get('FLASK_HOST') or '0.0.0.0'
port = environ.get('FLASK_PORT') or 5000

def taskManagerStarter():
    monkey.patch_all(socket=False, thread=False)
    controller = Controller()
    worker = Worker()
    server = zerorpc.Server(controller)
    server.bind("tcp://0.0.0.0:2017")
    worker.register_callback("start_callback", controller.worker_start_callback)
    worker.register_callback("end_callback", controller.worker_end_callback)
    joinall([spawn(server.run), spawn(worker.loop)])

if __name__ == '__main__':
    ''' proc = Process(target=taskManagerStarter)
    proc.start()  '''
    monkey.patch_all()
    app = create_app(sys.argv[1])
    http_server = WSGIServer((host, port), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
