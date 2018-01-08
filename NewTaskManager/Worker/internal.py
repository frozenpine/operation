# coding=utf-8
"""
Worker节点用于与内部工作进程通信的SocketServer
"""
import os
import SocketServer
import json
import ssl
from threading import Thread

from NewTaskManager.Worker import worker_logger as logging
from NewTaskManager.Worker.worker import msg_queue
from NewTaskManager.excepts import DeserialError
from NewTaskManager.protocol import TaskResult

internal_socket = dict()


class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):

    @staticmethod
    def process(data):
        try:
            task_result = TaskResult.deserial(data)
            logging.info(u'Server Receive : {0}'.format(json.dumps(task_result.to_dict(), ensure_ascii=False)))
            task_status = task_result.status_code
            if task_status.IsExcepted:
                msg_queue.put_event('except', task_result)
            if task_status.IsInited:
                msg_queue.put_event('init', task_result)
            if task_status.IsRunning:
                msg_queue.put_event('start', task_result)
            if task_status.IsDone:
                msg_queue.put_event('end', task_result)
            return 0
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
                self.request.sendall(ack)
                logging.info('Server Send: {0}'.format(ack))
            else:
                logging.warning('Server Disconnect: {0}'.format(self.client_address))
                break


class InternalSocketServer(Thread):

    def __init__(self, host, port):
        class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
            def __init__(self, server_address, request_handler, bind_and_activate=True):
                SocketServer.TCPServer.__init__(self, server_address, request_handler, bind_and_activate)
                self._server_cert = os.path.join(os.path.dirname(__file__), os.pardir, 'Certs', 'server.crt')
                self._server_key = os.path.join(os.path.dirname(__file__), os.pardir, 'Certs', 'server.key')
                self._ca_certs = os.path.join(os.path.dirname(__file__), os.pardir, 'Certs', 'ca.crt')

            def get_request(self):
                new_socket, from_address = self.socket.accept()
                conn_stream = ssl.wrap_socket(
                    new_socket, server_side=True, certfile=self._server_cert, keyfile=self._server_key,
                    ca_certs=self._ca_certs, ssl_version=ssl.PROTOCOL_TLSv1_2)
                return conn_stream, from_address

        Thread.__init__(self)

        self.socket_server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)

    def run(self):
        self.socket_server.serve_forever()
