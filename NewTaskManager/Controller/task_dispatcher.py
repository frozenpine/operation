# coding=utf-8

import SocketServer
import threading
# from gevent.threading import Thread

from multiprocessing import Queue
# from gevent.queue import Queue

from NewTaskManager.protocol import TmProtocol, TaskResult, TaskStatus, MSG_DICT
from NewTaskManager.excepts import DeserialError
from NewTaskManager.Controller import controller_logger as logging
from NewTaskManager.Controller.events import EventName


class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):
    def _process(self, data):
        if data.destination != 'MASTER':
            logging.error('Invalid destinated message received')

    def handle(self):
        while True:
            buff = self.request.recv(8192)
            if buff:
                try:
                    data = TmProtocol.deserial(buff)
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


class TaskDispatcher(threading.Thread):
    def __init__(self, host, port, event_queue):
        threading.Thread.__init__(self)
        self._event_queue = event_queue
        self._task_cache = Queue()
        self._server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)

    def run(self):
        self._server.serve_forever()

    def task_dispatch_callback(self, event):
        logging.info('Event received: {} {}'.format(event.Name, event.Data.to_dict()))
        self._task_cache.put_nowait(event.Data)
        self._event_queue.put_event(EventName.TaskResult, TaskResult(
            '123', '456', TaskStatus.Success, MSG_DICT[TaskStatus.Success], None))

    def _dispatcher(self):
        while True:
            task = self._task_cache.get()
            # if isinstance()
