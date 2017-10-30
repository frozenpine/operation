# -*- coding: utf-8 -*-
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from os import environ

import zerorpc
import zmq.green as zmq
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

from MessageQueue.msgserver import MessageQueues
from settings import config

sys.modules['zmq'] = zmq

''' logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S'
) '''

flask_logger = logging.getLogger('flask')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
flask_logger.addHandler(console)

Rthandler = TimedRotatingFileHandler(
    'Logs/flaskSyslog.log',
    when='midnight',
    interval=1,
    backupCount=15,
    encoding='utf-8'
)
Rthandler.setLevel(logging.WARN)
formatter = logging.Formatter(
    '%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s'
)
Rthandler.setFormatter(formatter)
flask_logger.addHandler(Rthandler)

db = SQLAlchemy()
db_list = {}

tm_host = environ.get('TM_HOST') or '127.0.0.1'
tm_port = environ.get('TM_PORT') or 6000

msgQueues = MessageQueues
globalEncryptKey = None
taskManager = zerorpc.Client()
taskManager.connect("tcp://{ip}:{port}".format(ip=tm_host, port=tm_port))
taskRequests = {}

from auth import auth as auth_blueprint, login_manager
from restful import restapi as restapi_blueprint

main = Blueprint('main', __name__)


def create_app(config_name):
    app = Flask(__name__)
    app_config = None
    import_str = 'from settings import {} as app_config'.format(config[config_name])
    try:
        exec import_str
    except ImportError:
        raise
    app.config.from_object(app_config)
    app_config.init_app(app)
    if app.config['GLOBAL_ENCRYPT']:
        globalEncryptkey = app.config['SECRET_KEY']

    login_manager.init_app(app)
    db.init_app(app)
    #db.create_all()

    app.register_blueprint(main)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(restapi_blueprint, url_prefix='/api')

    return app


from . import views, errors
