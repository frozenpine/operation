# -*- coding: UTF-8 -*-
import sys
from os import environ

from gevent import monkey
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from app import create_app

app_host = environ.get('FLASK_HOST') or '0.0.0.0'
app_port = environ.get('FLASK_PORT') or 6001


if __name__ == '__main__':
    monkey.patch_all()
    app = create_app(sys.argv[1])
    http_server = WSGIServer((app_host, int(app_port)), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
