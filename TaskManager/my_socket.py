# coding=utf-8

import pickle
import socket
from threading import Thread

from TaskManager import tm_logger as logging


class ParentPipe(Thread):
    def __init__(self, pipe_parent, init_callback, start_callback, end_callback):
        Thread.__init__(self)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('127.0.0.1', 7000))
        self.server.listen(10)
        self.init_callback = init_callback
        self.start_callback = start_callback
        self.end_callback = end_callback

    def run(self):
        """
        监听管道消息
        :return:
        """
        while True:
            client, address = self.server.accept()
            info = client.recv(102400)
            logging.info('socket receive info length: {0}'.format(len(info)))
            try:
                info = pickle.loads(info)
            except Exception, e:
                logging.warning('socket receive info deserialize error: {0}'.format(e))
                continue
            logging.info('socket receive: {0}'.format(info.to_str()))
            if info:
                if info.type() == "init":
                    self.init_callback(info)
                if info.type() == "start":
                    self.start_callback(info)
                if info.type() == "end":
                    self.end_callback(info)
            else:
                logging.warning('unexpected socket received: {0}'.format(info.to_str()))


class PipeChild(object):
    @staticmethod
    def send(data):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 7000))
        dump_data = pickle.dumps(data)
        logging.info('socket send info length: {0}'.format(len(dump_data)))
        try:
            client.send(dump_data)
        except Exception, e:
            logging.error('socket send error: {0}'.format(e))
            raise


def Pipe(duplex):
    return None, PipeChild()
