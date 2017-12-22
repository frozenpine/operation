# coding=utf-8
"""
Worker节点用于与Controller通信的SocketServer
"""

import json
import socket
import time
from threading import Thread

from NewTaskManager.Worker import worker_logger as logging
from NewTaskManager.Worker.worker import msg_queue
from NewTaskManager.excepts import DeserialError
from NewTaskManager.protocol import TmProtocol, Hello

external_socket = dict()


class ExternalSocketServer(Thread):

    def __init__(self, master_host, master_port):

        Thread.__init__(self)
        self.master_host, self.master_port = master_host, master_port
        self.socket_client = self.init_socket()

    def init_socket(self):
        try:
            socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            socket_client.connect((self.master_host, self.master_port))
            tm_hello = TmProtocol("worker", "master", Hello())
            socket_client.send(tm_hello.serial())
            logging.info('External Connect To Host: {0}, Port: {1}'.format(self.master_host, self.master_port))
        except socket.error, e:
            logging.error(e)
            logging.warning('External Connect Fail'.format())
        else:
            return socket_client

    def send(self, event):
        data = event.event_data
        tm_data = TmProtocol('worker', 'master', data)
        retry_count = 0
        while 1:
            try:
                self.socket_client.sendall(tm_data.serial())
                logging.info(u'Server Send {0}'.format(json.dumps(tm_data.to_dict(), ensure_ascii=False)))
                # ack = self.socket_client.recv(8192)
                # todo: 判断ack逻辑
            except socket.timeout:
                retry_count = retry_count + 1
                logging.info('External Timeout, Retry {0}'.format(retry_count))
            except socket.error:
                retry_count = retry_count + 1
                self.socket_client = self.init_socket()
            else:
                break

    @staticmethod
    def process(data):
        try:
            data = TmProtocol.deserial(data)
            logging.info('External Receive: {0}'.format(json.dumps(data.to_dict(), ensure_ascii=False)))
        except DeserialError, e:
            logging.warning('Task Deserialize Error: {0}'.format(e))
        else:
            src = data.source
            dest = data.destination
            task_info = data.payload
            msg_queue.put_event('task', task_info)

    def run(self):
        while True:
            try:
                data = self.socket_client.recv(8192)
                self.process(data)
            except socket.error:
                retry_count = 0
                while 1:
                    retry_count = retry_count + 1
                    logging.warning('External Disconnect, Retry {0}'.format(retry_count))
                    ret = self.init_socket()
                    if ret:
                        self.socket_client = ret
                        break
                    else:
                        time.sleep(5)
