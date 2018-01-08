# coding=utf-8
"""
Worker节点用于与Controller通信的SocketServer
"""

import json
import os
import socket
import ssl
import time
from threading import Thread

from NewTaskManager.Worker import worker_logger as logging
from NewTaskManager.Worker.worker import msg_queue
from NewTaskManager.excepts import DeserialError
from NewTaskManager.protocol import TmProtocol, Hello, Health

external_socket = dict()


class ExternalSocketServer(Thread):

    def __init__(self, master_host, master_port):

        Thread.__init__(self)
        self.master_host, self.master_port = master_host, master_port
        self.socket_client = self.init_ssl()
        self.init_socket()

    @staticmethod
    def init_ssl():
        try:
            socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            socket_client = ssl.wrap_socket(
                socket_client,
                ca_certs=os.path.join(os.path.dirname(__file__), os.pardir, 'Certs', 'ca.crt'),
                certfile=os.path.join(os.path.dirname(__file__), os.pardir, 'Certs', 'client.crt'),
                keyfile=os.path.join(os.path.dirname(__file__), os.pardir, 'Certs', 'client.key'),
                cert_reqs=ssl.CERT_REQUIRED, ssl_version=ssl.PROTOCOL_TLSv1_2
            )
        except Exception, e:
            logging.error('External Init SSL Fail: {0}'.format(e))
        else:
            return socket_client

    def init_socket(self):
        retry_count = 0
        while 1:
            retry_count = retry_count + 1
            ret = self.reconnect_socket()
            if ret == 0:
                break
            else:
                logging.warning('External Disconnect, Retry {0}'.format(retry_count))
                time.sleep(5)

    def reconnect_socket(self):
        try:
            self.socket_client.connect((self.master_host, self.master_port))
            logging.info('External Connect To Host: {0}, Port: {1}'.format(self.master_host, self.master_port))
        except socket.error:
            logging.warning('External Connect Fail')
            return -1
        else:
            self.hello()
            self.health()
            return 0

    @staticmethod
    def hello():
        msg_queue.put_event('hello', Hello())

    @staticmethod
    def health():
        msg_queue.put_event('health_query', Health(None, None, None))

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
                del self.socket_client
                self.socket_client = self.init_ssl()
                self.reconnect_socket()
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
                if not data:
                    raise socket.error
            except socket.error:
                retry_count = 0
                while 1:
                    retry_count = retry_count + 1
                    logging.warning('External Disconnect, Retry {0}'.format(retry_count))
                    # 删除原先的连接重连
                    del self.socket_client
                    self.socket_client = self.init_ssl()
                    ret = self.reconnect_socket()
                    if ret == 0:
                        break
                    else:
                        time.sleep(5)
            else:
                self.process(data)
