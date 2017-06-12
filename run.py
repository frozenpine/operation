# -*- coding: UTF-8 -*-
import sys
from os import environ

from gevent import monkey
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from app import create_app

monkey.patch_all()

host = environ.get('FLASK_HOST') or '0.0.0.0'
port = environ.get('FLASK_PORT') or 5000

if __name__ == '__main__':
    app = create_app(sys.argv[1])
    http_server = WSGIServer((host, port), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
