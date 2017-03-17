from .models import User
from flask import Flask, Blueprint
from flask_login import LoginManager
from settings import config
from auth import auth as auth_blueprint, login_manager
from restful import restapi as restapi_blueprint

main = Blueprint('main', __name__)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    login_manager.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(restapi_blueprint, url_prefix='/api')

    return app

from . import views, errors
