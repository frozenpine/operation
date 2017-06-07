# -*- coding: utf-8 -*-
import logging
import json
from enum import Enum
from sqlalchemy import create_engine
from app.models import CommandHistory
import arrow
import re

class CommandBuffer(object):
    def __init__(self, host, user, operator, app, websocket=None):
        self._websocket = websocket
        self._maxlines = 1000
        self._host = host
        self._user = user
        self._operator = operator
        self._db = create_engine(
            app.config['SQLALCHEMY_DATABASE_URI']
        ).connect()
        self.command_lines = []
        self.command_lines.append('')
        self.x = 0
        self.y = 0
        self.skip = False
        self._tab = False
        self.filter_keyword = [
            'stopall'
        ]
        self._interactive_commands = [
            'vim', 'vi', 'nano'
        ]
        self._interactive = False

    @property
    def CurrentCommand(self):
        if self.y >= len(self.command_lines):
            return None
        else:
            return self.command_lines[self.y]

    def ArrowLeft(self):
        if self.x - 1 >= 0:
            self.x -= 1
        else:
            self.x = 0

    def ArrowRight(self):
        if self.CurrentCommand:
            if self.x + 1 <= len(self.CurrentCommand):
                self.x += 1
            else:
                self.x = len(self.CurrentCommand)

    def ArrowUp(self):
        if self.y - 1 >= 0:
            self.y -= 1
        else:
            self.y = 0
        self.x = len(self.CurrentCommand)

    def ArrowDown(self):
        if self.y + 1 <= self._maxlines:
            self.y += 1
        else:
            self.y = self._maxlines
        if self.CurrentCommand:
            self.x = len(self.CurrentCommand)

    def Ctrl_A(self):
        self.x = 0

    def Ctrl_E(self):
        self.x = len(self.CurrentCommand)

    def Ctrl_C(self):
        pass

    def Home(self):
        self.Ctrl_A()

    def End(self):
        self.Ctrl_E()

    def Backspace(self):
        if self.x >= len(self.CurrentCommand):
            self.command_lines[self.y] = self.CurrentCommand[:-1]
        elif self.x > 0:
            self.command_lines[self.y] = self.CurrentCommand[:self.x - 1] + \
                self.CurrentCommand[self.x:]
        self.ArrowLeft()

    def Delete(self):
        self.command_lines[self.y] = self.CurrentCommand[:self.x] + \
            self.CurrentCommand[self.x + 1:]

    def Esc(self):
        pass

    def Enter(self):
        if self.y + 1 >= self._maxlines:
            self.y -= 499
            self.command_lines = self.command_lines[500:]
        if self.CurrentCommand in self.filter_keyword:
            self.skip = True
        else:
            self.skip = False
        if self.CurrentCommand.split(' ')[0] in self._interactive_commands:
            self._interactive = True
        if self.CurrentCommand != '':
            try:
                command = "INSERT INTO command_histories\
                    (command_line, host, username, operator_id, operated_at, skip) \
                    VALUES('{command_line}', '{host}', '{username}', {operator_id}, \
                    '{operated_at}', {skip})".format(
                        command_line=self.CurrentCommand,
                        host=self._host,
                        username=self._user,
                        operator_id=self._operator.id,
                        operated_at=arrow.now(),
                        skip=self.skip and 1 or 0
                    )
                self._db.execute(command)
            except Exception as err:
                logging.warning(err.message)
            if self.y < len(self.command_lines) - 1:
                self.command_lines[-1] = self.CurrentCommand
            if self.skip:
                self.command_lines.pop()
            self.command_lines.append('')
            self.y = len(self.command_lines) - 1

    def Tab(self):
        self._tab = True

    def handle_response(self, response):
        try:
            EscapeKey(response)
        except ValueError:
            if not re.match(r'^[\x00-\x1f\x7f]$', response) \
                and self._tab and not self._interactive and '\n' not in response:
                self.command_lines[self.y] = self.CurrentCommand[:self.x] + \
                    response.replace('\x07', '') + self.CurrentCommand[self.x:]
                self.x += len(response)
                self.ArrowRight()
            if self._interactive and '\x07' in response:
                '''
                退出交互式编辑界面时，终端会发送ASCII BELL指令
                '''
                self._interactive = False
                self.x = 0
            if self._tab:
                self._tab = False
        finally:
            return response

    def handle_key(self, key):
        try:
            esckey = EscapeKey(key)
        except ValueError:
            if re.match(r'[\x20-\x7e]', key) and not self._interactive:
                self.command_lines[self.y] = self.CurrentCommand[:self.x] + \
                    key + self.CurrentCommand[self.x:]
                self.ArrowRight()
        else:
            method = getattr(self, esckey.name)
            if method:
                method()
            if self.skip:
                self.skip = False
                if self._websocket:
                    self._websocket.send(json.dumps({
                        'data': '\x1b[01;31mcommand not allowed due to web shell policy.\x1b[0m'
                    }))
                key = EscapeKey.Ctrl_C.value
        finally:
            return key

class EscapeKey(Enum):
    ArrowUp = u'\x1b[A'
    ArrowDown = u'\x1b[B'
    ArrowRight = u'\x1b[C'
    ArrowLeft = u'\x1b[D'
    Ctrl_A = u'\x01'
    Ctrl_E = u'\x05'
    Ctrl_C = u'\x03'
    Home = u'\x1bOH'
    End = u'\x1bOF'
    Backspace = u'\x7f'
    Esc = u'\x1b'
    Enter = u'\r'
    Tab = u'\t'
