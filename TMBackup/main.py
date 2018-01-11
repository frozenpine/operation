# coding=utf-8

import sys
from os import environ, path

import gevent
import zerorpc
from gevent import monkey

try:
    from TMBackup.controller import Controller
    from TMBackup.worker import Worker
    from TMBackup.socket_conn import SocketServer
except ImportError:
    sys.path.append(path.join(path.dirname(sys.argv[0]), "../"))
    from TMBackup.controller import Controller
    from TMBackup.worker import Worker
    from TMBackup.socket_conn import SocketServer

tm_host = environ.get("TM_HOST") or "0.0.0.0"
tm_port = environ.get("TM_PORT") or 6000
socket_port = environ.get("SOCKET_PORT") or 7000
socket_timeout = environ.get("SOCKET_TIMEOUT") or 5

monkey.patch_all(socket=False, thread=False, time=False, subprocess=False)

if __name__ == "__main__":
    controller = Controller()
    controller.deserialize()
    worker = Worker()
    server = zerorpc.Server(controller)
    server.bind("tcp://{ip}:{port}".format(ip=tm_host, port=tm_port))
    worker.register_callback("init_callback", controller.worker_init_callback)
    worker.register_callback("start_callback", controller.worker_start_callback)
    worker.register_callback("end_callback", controller.worker_end_callback)
    SocketServer(controller.worker_init_callback, controller.worker_start_callback, controller.worker_end_callback,
                 socket_port).start()
    controller.register_callback("kill_callback", worker.kill_process_callback)
    gevent.joinall([gevent.spawn(server.run), gevent.spawn(worker.loop)])