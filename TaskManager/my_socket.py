# coding=utf-8

import pickle
import socket
import time
from threading import Thread

from TaskManager import tm_logger as logging


class SocketServer(Thread):
    def __init__(self, init_callback, start_callback, end_callback):
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
            # 计算收到的消息消息长度
            logging.info('[server] info length: {0}'.format(len(info)))
            try:
                info = pickle.loads(info)
            except Exception, e:
                logging.warning('[server] info deserialize error: {0}'.format(e))
                continue
            logging.info('[server] receive: {0}'.format(info.to_str()))
            try:
                client.send('ok')
            except Exception, e:
                logging.warning('[server] send ok error: {0}'.format(e))
            if info:
                if info.type() == "init":
                    self.init_callback(info)
                if info.type() == "start":
                    self.start_callback(info)
                if info.type() == "end":
                    self.end_callback(info)
            else:
                logging.warning('unexpected socket received: {0}'.format(info.to_str()))


class SocketClient(object):
    @classmethod
    def send(cls, data):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 7000))
        dump_data = pickle.dumps(data)
        # 计算dump之后消息长度
        logging.info('[client] info length: {0}'.format(len(dump_data)))
        logging.debug('[client] info: {0}'.format(dump_data))
        retry_count = 0
        while 1:
            client.settimeout(2.0)
            try:
                client.send(dump_data)
            except Exception, e:
                # 因server端socket异常未正常发送
                logging.warning('[client] send info error: {0}'.format(e))
                raise
            try:
                ack = client.recv(102400)
            except socket.timeout:
                # 未收到server端确认信息
                retry_count += 1
                logging.warn('[client] retry: {0}'.format(retry_count))
            else:
                break
        # 收到server端确认消息
        logging.info('[client] receive ack: {0}'.format(ack))
        client.close()
