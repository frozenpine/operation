from app import app
from flask import Flask, render_template
from forms import LoginForm

@app.route('/hello', methods=['GET'])
def hello_world():
    return 'Hello World!'

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'sonny'}
    return render_template("index.html", title='home', user=user)

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='login', form=form)
