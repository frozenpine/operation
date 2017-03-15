from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('settings')

login_manager = LoginManager()
login_manager.session_protection = 'Strong'
login_manager.login_view = 'login'
login_manager.init_app(app)

from app import views, models
from restful import uris
