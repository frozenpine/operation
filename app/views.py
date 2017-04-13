# -*- coding: UTF-8 -*-
from . import main
from flask import Flask, render_template, request, flash, redirect, url_for, g
from flask_login import login_required, current_user
from forms import DeviceForm
from .models import User, TradeSystem

user = ""

@main.route('/hello')
@main.route('/hello/<string:name>')
def hello_world(**kwargs):
    global user
    if kwargs.has_key('name'):
        user = kwargs['name']
    return render_template('hello.html', name=user)

@main.route('/')
@main.route('/index')
@login_required
def index():
    return render_template("index.html", title='ITIL Test')

@main.route('/UI/views/<string:name>')
@login_required
def UIView(name):
    return render_template("{}.html".format(name))
