# coding=utf-8
"""
Worker节点用于与Controller通信的SocketServer
"""

import json
import socket
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
        retry_count = 0
        while 1:
            try:
                socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_client.connect((self.master_host, self.master_port))
                tm_hello = TmProtocol("worker", "master", Hello())
                socket_client.settimeout(2)
                socket_client.send(tm_hello.serial())
                logging.info('Server Connect To Host: {0}, Port: {1}'.format(self.master_host, self.master_port))
            except socket.error, e:
                retry_count = retry_count + 1
                logging.error(e)
                logging.warning('Server Connect Fail, Retry {0}'.format(retry_count))
            else:
                return socket_client

    def send(self, event):
        data = event.event_data
        tm_data = TmProtocol('worker', 'master', data)
        retry_count = 0
        while 1:
            try:
                self.socket_client.send(tm_data.serial())
                logging.info(u'Server Send {0}'.format(json.dumps(tm_data.to_dict(), ensure_ascii=False)))
                # ack = self.socket_client.recv(8192)
                # todo: 判断ack逻辑
            except socket.timeout:
                retry_count = retry_count + 1
                logging.info('Server Timeout, Retry {0}'.format(retry_count))
            except socket.error:
                retry_count = retry_count + 1
                self.socket_client = self.init_socket()
            else:
                break

    def process(self, data):
        try:
            data = TmProtocol.deserial(data)
            logging.info('Socket Receive: {0}'.format(json.dumps(data.to_dict(), ensure_ascii=False)))
        except DeserialError, e:
            logging.warning('Task Deserialize Error: {0}'.format(e))
        else:
            src = data.source
            dest = data.destination
            task_info = data.payload
            if src not in external_socket:
                external_socket.update({src: self.request})
            msg_queue.put_event('task', task_info)

    def run(self):
        while True:
            data = self.socket_client.recv(8192)
            if data:
                self.process(data)
            else:
                logging.warning('Socket Disconnect: {0}'.format(self.client_address))
                break
