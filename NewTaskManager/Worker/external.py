# coding=utf-8
"""
Worker节点用于与Controller通信的SocketServer
"""

import SocketServer
from threading import Thread

from NewTaskManager.Worker import worker_logger as logging
from NewTaskManager.Worker.worker import msg_queue
from NewTaskManager.excepts import DeserialError
from NewTaskManager.protocol import TmProtocol

external_socket = dict()


class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):

    def process(self, data):
        try:
            data = TmProtocol.deserial(data)
        except DeserialError, e:
            logging.warning('Task Deserialize Error: {0}'.format(e))
        else:
            src = data.source
            dest = data.destination
            task_info = data.payload
            if src not in external_socket:
                external_socket.update({src: self.request})
            msg_queue.put_event('task', task_info)

    def handle(self):
        while True:
            data = self.request.recv(8192)
            if data:
                self.process(data)
                logging.debug('Socket Receive: {0}'.format(data))
            else:
                logging.warning('Socket Disconnect: {0}'.format(self.client_address))
                break


class ExternalSocketServer(Thread):

    def __init__(self, host, port):
        class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
            pass

        Thread.__init__(self)

        self.socket_server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)

    @staticmethod
    def send(event):
        pass

    def run(self):
        self.socket_server.serve_forever()
