# -*- coding: UTF-8 -*-
from flask_wtf import Form
from wtforms import (StringField, BooleanField, PasswordField, SelectField, IntegerField)
from wtforms.validators import DataRequired, Length
#from app.models import User, Operator

class LoginForm(Form):
    login = StringField('login', validators=[DataRequired()], render_kw={'placeholder': u'输入账户'})
    password = PasswordField('password', validators=[DataRequired()], render_kw={'placeholder': u'输入密码'})
    remember_me = BooleanField('remember_me', default=False)

class RegisterForm(Form):
    name = StringField('name', validators=[DataRequired(), Length(min=1,max=20)])
    login = StringField('login', validators=[DataRequired(), Length(min=1,max=20)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6, max=20)])
    #sex = SelectField('sex', validators=[DataRequired()], choices=User.SEX)
