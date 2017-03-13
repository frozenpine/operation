from app import app
from flask import Flask, render_template, request, flash, redirect, session, url_for
from forms import LoginForm
from .models import User

@app.route('/hello')
def hello_world():
    return 'Hello World!'

@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        user = {'name': session['username']}
    else:
        user = {'name': 'guest'}
    return render_template("index.html", title='home', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'login_name' in session:
        flash('Already logged in.')
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            try:
                user = User.nodes.get(login=form.login.data)
                if form.password.data == user.password:
                    session['username'] = user.name
                    return redirect(url_for('index'))
                else:
                    flash("Invalid password!")
            except User.DoesNotExist:
                flash("Invalid Login Name!")
        else:
            flash("Invalid input data!")
    return render_template('login.html', title='login', form=form)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
