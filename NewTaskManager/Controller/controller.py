# coding=utf-8

import sys
from multiprocessing import Queue
from multiprocessing import Process
from os import environ, path

sys.path.append(path.join(path.dirname(__file__), '../'))
from NewTaskManager.Controller.task_queue_manager import TaskQueueManager
''' from .msg_loop import MessageLoop
from .socket_server import ControllerSocketServer '''

# msg_queue = Queue()


class Controller(Process):
    def __init__(self):
        rpc_addr = environ.get('TM_HOST') or '0.0.0.0'
        rpc_port = environ.get('TM_PORT') or 6000
        # socket_port = environ.get("SOCKET_PORT") or 7000
        # socket_host = environ.get("SOCKET_HOST") or '0.0.0.0'
        self._rpc_server = TaskQueueManager(rpc_addr, rpc_port)
        # self._socket_server = ControllerSocketServer(socket_host, socket_port)
        # self._msg_loop = MessageLoop()
        self._to_taskqueue_manager = Queue()
        self._to_socket_server = Queue()
        self._to_rpc_server = Queue()

    def run(self):
        self._rpc_server.daemon = True
        # self._socket_server.daemon = True
        self._rpc_server.run()
        # self._socket_server.run()
        # self._msg_loop.register_callback
