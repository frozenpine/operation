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
from NewTaskManager.protocol import TmProtocol, Task, TaskResult, TaskStatus, MSG_DICT, Heartbeat, Hello
from NewTaskManager.excepts import DeserialError
from SysManager.configs import Result


class SocketClient(object):
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        conn = ('localhost', 7000)
        self._socket.connect(conn)
        self.Send(Hello())

    def Send(self, payload):
        return self._socket.sendall(TmProtocol(src='work_sim', dest='MASTER', payload=payload).serial())

    def Receive(self, buff_size=8192):
        buff = self._socket.recv(buff_size)
        try:
            proto = TmProtocol.deserial(buff)
        except DeserialError as err:
            logging.warning(err.message)
        return proto.payload

    def Close(self):
        return self._socket.close()

if __name__ == '__main__':
    client = SocketClient()
    while True:
        try:
            payload = client.Receive()
        except:
            logging.error('socket disconnect')
            break
        if isinstance(payload, Task):
            logging.info('Task from server: {}'.format(payload.to_dict()))
            time.sleep(1)
            client.Send(TaskResult(
                payload.queue_uuid, payload.task_uuid, TaskStatus.Running,
                MSG_DICT[TaskStatus.Running], payload.session))
            time.sleep(3)
            result = Result()
            result.data = {}
            result.return_code = 0
            result.lines = ['result from worker_sim']
            result.error_msg = u'成功'
            client.Send(TaskResult(
                payload.queue_uuid, payload.task_uuid, TaskStatus.Success,
                MSG_DICT[TaskStatus.Success], payload.session, result))
