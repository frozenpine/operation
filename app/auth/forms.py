# -*- coding: UTF-8 -*-
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField
from wtforms.validators import DataRequired, Length


#from app.models import User

class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()], render_kw={'placeholder': u'输入账户'})
    password = PasswordField(
        'password',
        validators=[DataRequired()],
        render_kw={'placeholder': u'输入密码'}
    )
    remember_me = BooleanField('remember_me', default=False)

class RegisterForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=1, max=20)])
    login = StringField('login', validators=[DataRequired(), Length(min=1, max=20)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6, max=20)])
    #sex = SelectField('sex', validators=[DataRequired()], choices=User.SEX)
