# -*- coding: UTF-8 -*-
from flask_wtf import Form
from wtforms import (StringField, BooleanField, PasswordField, SelectField, IntegerField)
from wtforms.validators import DataRequired, Length
from app.models import Device

class DeviceForm(Form):
    name = StringField('name', validators=[DataRequired(), Length(min=1,max=100)])
    model = StringField('name', validators=[Length(min=-1,max=100)])
    serial_num = StringField('name', validators=[Length(min=-1,max=100)])
    status = SelectField('status', validators=[DataRequired()], choices=Device.STATUS)
    warranty = IntegerField('warranty')
