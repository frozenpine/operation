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
from SysManager import Task


class SocketClient(object):
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        conn = ('localhost', 7000)
        self._socket.connect(conn)
        # timer = threading.Timer(4 + random.random(), SocketClient._heartbeat, [self])
        # timer.setDaemon(True)
        # timer.start()
        # self.Send(Heartbeat())
        self.Send(Hello())

    ''' @staticmethod
    def _heartbeat(socket_client):
        socket_client.Send(Heartbeat())
        timer = threading.Timer(5 + random.random(), SocketClient._heartbeat, [socket_client])
        timer.setDaemon(True)
        timer.start() '''

    def Send(self, payload):
        return self._socket.sendall(TmProtocol(src='work_sim', dest='MASTER', payload=payload).serial())

    def Receive(self, buff_size=8192):
        buff = self._socket.recv(buff_size)
        try:
            proto = TmProtocol.deserial(buff)
        except DeserialError as err:
            logging.warning(err.message)
        # logging.info('source: {}, dest: {}'.format(proto.source, proto.destination))
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
                MSG_DICT[TaskStatus.Running], payload.session, {}))
            time.sleep(3)
            client.Send(TaskResult(
                payload.queue_uuid, payload.task_uuid, TaskStatus.Success,
                MSG_DICT[TaskStatus.Success], payload.session, {}}))
        if isinstance(payload, Heartbeat):
            logging.info('Heart beat from server')
