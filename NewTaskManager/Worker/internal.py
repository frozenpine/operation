# coding=utf-8
"""
Worker节点用于与内部工作进程通信的SocketServer
"""

import SocketServer
import json
import socket
from threading import Thread

from NewTaskManager.Worker import worker_logger as logging
from NewTaskManager.excepts import DeserialError
from NewTaskManager.protocol import TaskResult

internal_socket = dict()


class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):

    @staticmethod
    def process(data):
        try:
            task_result = TaskResult.deserial(data)
            return task_result
        except DeserialError:
            logging.error('TaskResult Deserialize Error')
            return -1

    def handle(self):
        while True:
            data = self.request.recv(8192)
            if data:
                logging.info('Server Receive Len: {0}'.format(len(data)))
                ret = self.process(data)
                if ret != -1:
                    ack = '{"ack": "Pass"}'
                else:
                    ack = '{"ack": "Fail"}'
                self.request.send(ack)
                logging.info('Server Send: {0}'.format(ack))
            else:
                logging.warning('Server Disconnect: {0}'.format(self.client_address))
                break


class InternalSocketServer(Thread):

    def __init__(self, host, port):
        class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
            pass

        Thread.__init__(self)

        self.socket_server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)

    @staticmethod
    def send(socket_id, data):
        if isinstance(data, dict):
            data = json.dumps(data)
            try:
                internal_socket.get(socket_id).send(data)
            except socket.error, e:
                internal_socket.pop(socket_id)
                logging.info('Socket Disconnect: {0}'.format(socket_id))
        else:
            logging.warning('Socket Send Format Error: {0}'.format(data))

    def run(self):
        self.socket_server.serve_forever()
