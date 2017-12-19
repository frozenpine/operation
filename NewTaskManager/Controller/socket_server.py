# coding=utf-8

import SocketServer
import json
import socket
from threading import Thread

from enum import Enum

from NewTaskManager.Controller import controller_logger as logging
from NewTaskManager.protocol import TmProtocol
from NewTaskManager.excepts import *


class MessageType(Enum):
    CONNECT = 101
    HEARTBEAT = 102
    DISCONNECT = 103


SOCKET_CACHE = {}


class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):
    def _process(self, data):
        ''' if data.get('MessageType') == MessageType.CONNECT.value:
            SOCKET_CACHE.update({data.get('SocketID'): self.request})
            return 0
        if data.get('MessageType') == MessageType.HEARTBEAT.value:
            pass
        if data.get('MessageType') == MessageType.DISCONNECT.value:
            logging.info('[socket] disconnect: {0}'.format(self.client_address))
            SOCKET_CACHE.pop(data.get('SocketID'))
            self.request.close()
            return -1 '''
        if data.destination != 'MASTER':
            logging.error('Invalid destinated message received')

    def handle(self):
        while True:
            buff = self.request.recv(8192)
            if buff:
                try:
                    # data = json.loads(data)
                    data = TmProtocol.deserial(buff)
                    # logging.info('[socket] receive: {0}'.format(data))
                except DeserialError as err:
                    logging.warning('[socket] format error: {0}'.format(err.message))
                else:
                    ret = self._process(data)
                    if ret == -1:
                        break
            else:
                logging.warning('[socket] disconnect: {0}'.format(self.client_address))
                break


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


class ControllerSocketServer(Thread):

    def __init__(self, host, port):
        super(ControllerSocketServer, self).__init__()
        self.socket_server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)

    @staticmethod
    def send(socket_id, data):
        if isinstance(data, dict):
            data = json.dumps(data)
            try:
                SOCKET_CACHE.get(socket_id).send(data)
            except socket.error, e:
                SOCKET_CACHE.pop(socket_id)
                logging.info('[socket] disconnect: {0}'.format(socket_id))
        else:
            logging.warning('[socket] format error: {0}'.format(data))

    def run(self):
        self.socket_server.serve_forever()


if __name__ == '__main__':
    p = ControllerSocketServer('127.0.0.1', 7000)
    p.start()
