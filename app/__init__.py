from flask import Flask

app = Flask(__name__)
app.config.from_object('settings')

from app import views, models
from restful import uris
