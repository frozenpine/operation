from test import app
from flask import render_template

@app.route('/hello')
def hello_world():
    return 'Hello World!'

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'sonny'}
    return render_template("index.html", title='home', user=user)