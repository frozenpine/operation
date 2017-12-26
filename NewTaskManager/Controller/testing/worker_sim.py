# coding=utf-8

import sys
import os
import socket
import logging
import time
import random
import threading

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S'
)

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
from NewTaskManager.protocol import TmProtocol, Task, TaskResult, TaskStatus, MSG_DICT, Heartbeat, Hello, Health
from NewTaskManager.excepts import DeserialError
from SysManager.configs import Result


class SocketClient(object):
    def __init__(self):
        self._conn = ('localhost', 7000)
        self.Connect()

    def Connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        try:
            self._socket.connect(self._conn)
        except socket.error:
            self.Reconnect()
        self.Send(Hello())
        self.Send(Health())

    def Reconnect(self, timeout=3):
        self._socket.close()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        while True:
            try:
                self._socket.connect(self._conn)
            except socket.error as err:
                logging.warning('Connect to server fail, retry in {}s'.format(timeout))
                time.sleep(timeout)
            else:
                self.Send(Hello())
                self.Send(Health())
                break

    def Send(self, payload):
        return self._socket.sendall(TmProtocol(src='work_sim', dest='MASTER', payload=payload).serial())

    def Receive(self, buff_size=8192):
        buff = self._socket.recv(buff_size)
        if buff:
            try:
                proto = TmProtocol.deserial(buff)
            except DeserialError as err:
                logging.warning(err.message)
            return proto.payload
        else:
            return None

    def Close(self):
        return self._socket.close()

if __name__ == '__main__':
    client = SocketClient()
    while True:
        try:
            payload = client.Receive()
        except socket.error:
            logging.error('socket disconnect')
            client.Reconnect()
        else:
            if isinstance(payload, Task):
                logging.info('Task from server: {}'.format(payload.to_dict()))
                time.sleep(1)
                client.Send(TaskResult(
                    payload.queue_uuid, payload.task_uuid, TaskStatus.Running,
                    MSG_DICT[TaskStatus.Running], payload.session))
                time.sleep(3)
                result = Result()
                result.data = {}
                if payload.task_info['mod']['shell'] == 'startall':
                    result.return_code = 1
                    result.lines = ['fail simu from worker_sim']
                    result.error_msg = u'失败'
                else:
                    result.return_code = 0
                    result.lines = ['result from worker_sim']
                    result.error_msg = u'成功'
                client.Send(TaskResult(
                    payload.queue_uuid, payload.task_uuid,
                    TaskStatus.Success if result.return_code == 0 else TaskStatus.Failed,
                    MSG_DICT[TaskStatus.Success], payload.session, result))
