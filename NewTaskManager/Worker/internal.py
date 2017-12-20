# coding=utf-8
"""
Worker节点用于与内部工作进程通信的SocketServer
"""

import SocketServer
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
            task_status = task_result.status_code
            if task_status.IsInited:
                msg_queue.put_event('init', task_result)
                logging.info('MsgLoop Put Init {0}'.format(task_result))
            if task_status.IsRunning:
                msg_queue.put_event('start', task_result)
                logging.info('MsgLoop Put Run {0}'.format(task_result))
            if task_status.IsDone:
                msg_queue.put_event('end', task_result)
                logging.info('MsgLoop Put End {0}'.format(task_result))
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

    def run(self):
        self.socket_server.serve_forever()
