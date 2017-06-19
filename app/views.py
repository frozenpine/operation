# -*- coding: UTF-8 -*-
import json
import logging
from time import time

from flask import Response, abort, current_app, render_template, request
from flask_login import current_user, login_required
from geventwebsocket import WebSocketError

from app.auth.privileged import CheckPrivilege
from common import wssh
from common.cmdbuffer import CommandBuffer
from MessageQueue.msgserver import MessageServer
from models import MethodType, Operator

from . import main

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
    if name == 'emerge_ops' and \
        not CheckPrivilege(current_user, '/api/emerge_ops', MethodType.Authorize):
        return render_template("errors/403.html")
    return render_template("{}.html".format(name))

class Camera():
    def __init__(self):
        self.frames = [open('app/static/img/a{}.png'.format(f+1), 'rb').read() for f in xrange(10)]

    def get_frame(self):
        return self.frames[int(time()) % 10]

def _flowTest(camera):
    while True:
        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n'
               + camera.get_frame()
               + b'\r\n')

@main.route('/flow')
def flow():
    return Response(
        _flowTest(Camera()),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@main.route('/websocket')
@login_required
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
            cmdbuffer = CommandBuffer(
                '192.168.101.126', 'qdam',
                Operator.find(login='test'),
                current_app, ws
            )
            bridge = wssh.WSSHBridge(ws, cmdbuffer)
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
