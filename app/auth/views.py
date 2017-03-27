from . import auth
from .forms import LoginForm, RegisterForm
from flask import flash, request, redirect, url_for, render_template
from flask_login import login_required, login_user, current_user, logout_user
from app import db
from app.models import User, Operator

@auth.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Already logged in.')
        return redirect(url_for('main.index'))
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            '''
            try:
                user = User.nodes.get(login=form.login.data)
                if user.verify_password(form.password.data):
                    login_user(user, form.remember_me.data)
                    return redirect(request.args.get('next') or url_for('main.index'))
                else:
                    flash("Invalid password!")
            except User.DoesNotExist:
                flash("Invalid Login Name!")
            '''
            user = Operator.find(login=form.login.data)
            if user and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
            else:
                flash("Invalid login or password!")
        else:
            flash("Invalid input data!")
    return render_template('login.html', title='Login', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate():
            #usr = User.find(login=form.login.data)
            usr = Operator.find(login=form.login.data)
            if usr:
                flash("User({0}) \"{1}\" already exists!".format(usr.uuid, usr.name))
            else:
                try:
                    '''
                    user = User(login=form.login.data, name=form.name.data, 
                                password=form.password.data, sex=form.sex.data).save()
                    '''
                    user = Operator(form.login.data, form.password.data, form.name.data)
                    db.session.add(user)
                    db.session.commit()
                    login_user(user, True)
                    return redirect(url_for('main.index'))
                except:
                    flash('Registe failed, please contact administrator.')
        else:
            flash("Invalid input data!")
    return render_template('register.html', title='Register', form=form)
