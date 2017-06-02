# -*- coding: UTF-8 -*-
import logging
from geventwebsocket import WebSocketError
from flask import render_template, request, abort
from flask_login import login_required, current_user
from . import main
from MessageQueue.msgserver import MessageServer
import json
import wssh

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
    return render_template(
        "index.html", title='ITIL Test',
        user_name=current_user.name,
        user_id=current_user.id,
        user_login=current_user.login
    )

@main.route('/UI/views/<string:name>')
@login_required
def UIView(name):
    return render_template("{}.html".format(name))

@main.route('/websocket')
def websocket():
    if request.environ.has_key('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        if ws:
            while True:
                MessageServer.parse_request(ws)
        else:
            abort(500)

@main.route('/webshell')
def webshell():
    if request.environ.has_key('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        if ws:
            bridge = wssh.WSSHBridge(ws)
            try:
                bridge.open(
                    hostname='192.168.101.126',
                    username='qdam',
                    password='qdam'
                )
            except Exception:
                ws.send(json.dumps({
                    'message': 'can not connect to server.'
                }))
            else:
                bridge.shell()
            finally:
                return {
                    'message': 'webshell closed.'
                }
