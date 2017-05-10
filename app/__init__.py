import logging
from flask import Flask, Blueprint
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from settings import config
from MessageQueue.msgserver import MessageQueues

db = SQLAlchemy()
db_list = {}
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
