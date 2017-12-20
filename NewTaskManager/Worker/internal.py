# coding=utf-8
"""
Worker节点用于与内部工作进程通信的SocketServer
"""

import SocketServer
import json
import pickle
import socket
from threading import Thread

from enum import Enum

from NewTaskManager.Controller import controller_logger as logging

internal_socket = dict()


class MessageType(Enum):
    CONNECT = 101
    INFO = 102
    DISCONNECT = 103


class Protocol(object):
    def __init__(self, message_type, message_info):
        self.message_type = message_type
        self.message_info = message_info

    def to_dict(self):
        return {'MessageType': self.message_type,
                'MessageInfo': self.message_info}

    def serialize(self, to_json=False):
        if to_json:
            return json.dumps(self.to_dict())
        else:
            return pickle.dumps(self.to_dict())


class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):

    def process(self, data):
        if data.get('MessageType') == MessageType.CONNECT.value:
            internal_socket.update({data.get('SocketID'): self.request})
            return 0
        if data.get('MessageType') == MessageType.INFO.value:
            pass
        if data.get('MessageType') == MessageType.DISCONNECT.value:
            logging.info('Socket Disconnect: {0}'.format(self.client_address))
            internal_socket.pop(data.get('SocketID'))
            self.request.close()
            return -1

    def handle(self):
        while True:
            data = self.request.recv(8192)
            if data:
                self.request.send()
                try:
                    data = json.loads(data)
                    logging.info('Socket Receive: {0}'.format(data))
                except TypeError, e:
                    logging.warning('Socket Send Format Error: {0}'.format(data))
                else:
                    ret = self.process(data)
                    if ret == -1:
                        break
            else:
                logging.warning('Socket Disconnect: {0}'.format(self.client_address))
                break
            self.request.send(102, None)


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
