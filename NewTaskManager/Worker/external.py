# coding=utf-8
"""
Worker节点用于与Controller通信的SocketServer
"""

import SocketServer
import json
import socket
from threading import Thread

from NewTaskManager.Worker import worker_logger as logging
from NewTaskManager.Worker.worker import msg_queue
from NewTaskManager.excepts import DeserialError
from NewTaskManager.protocol import TmProtocol

external_socket = dict()
# 初始化Task

from NewTaskManager.protocol import Task

task = Task(
    queue_uuid='queue1',
    create_time='10:00',
    trigger_time='10:00',
    task_uuid='task1',
    task_info={
        "remote": {
            "params": {
                "ip": "192.168.100.90",
                "password": "qdam",
                "user": "qdam"
            },
            "name": "SSHConfig"
        },
        "mod": {
            "shell": "sleep 5",
            "name": "shell"
        }
    },
    task_earliest='10:00',
    task_latest='18:00',
    session='session'
)


class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):
    msg_queue.put_event('task', task)


    def process(self, data):
        try:
            data = TmProtocol.deserial(data)
        except DeserialError, e:
            logging.warning('Task Deserialize Error: {0}'.format(e))
        else:
            src = data.src
            dest = data.dest
            task_info = data.payload
            if src not in external_socket:
                external_socket.update({src: self.request})
            msg_queue.put('task', task_info)

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
    def send(socket_id, data):
        if isinstance(data, dict):
            data = json.dumps(data)
            try:
                external_socket.get(socket_id).send(data)
            except socket.error, e:
                external_socket.pop(socket_id)
                logging.info('Socket Disconnect: {0}'.format(socket_id))
        else:
            logging.warning('Socket Send Format Error: {0}'.format(data))

    def run(self):
        self.socket_server.serve_forever()
