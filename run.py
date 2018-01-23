# -*- coding: UTF-8 -*-
""" Flask server entrypoint """
import sys
from os import environ

from gevent import monkey
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from app import create_app

APP_HOST = environ.get('FLASK_SVR') or '0.0.0.0'
APP_PORT = environ.get('FLASK_PORT') or 6001


if __name__ == '__main__':
    monkey.patch_all()
    APP = create_app(sys.argv[1])
    HTTP_SERVER = WSGIServer((APP_HOST, int(APP_PORT)), APP, handler_class=WebSocketHandler)
    HTTP_SERVER.serve_forever()
