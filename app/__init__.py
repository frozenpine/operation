import logging
from flask import Flask, Blueprint
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from settings import config
from MessageQueue.msgserver import MessageQueues
<<<<<<< HEAD

db = SQLAlchemy()
=======
import logging
from logging.handlers import TimedRotatingFileHandler

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='Logs/Syslog.log',
    filemode='a'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

Rthandler = TimedRotatingFileHandler(
    'Logs/Syslog.log',
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
logging.getLogger('').addHandler(Rthandler)

db = SQLAlchemy()
db_list = {}
>>>>>>> 4-qdiam-special
msgQueues = MessageQueues

from auth import auth as auth_blueprint, login_manager
from restful import restapi as restapi_blueprint

main = Blueprint('main', __name__)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

    login_manager.init_app(app)
    db.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(restapi_blueprint, url_prefix='/api')

    return app

from . import views, errors
