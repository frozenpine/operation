from app import app
from flask import Flask, render_template, request, flash, redirect
from forms import LoginForm
from .models import User

@app.route('/hello')
def hello_world():
    return 'Hello World!'

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'sonny'}
    return render_template("index.html", title='home', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.validate():
            redirect('/index')
        else:
            flash('Invalid input.')
    else:
        form = LoginForm()
        return render_template('login.html', title='login', form=form)
