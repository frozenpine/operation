# coding=utf-8


import sys
from os import path, environ

import gevent
import zerorpc
from gevent import monkey

from controller import Controller
from worker import Worker

sys.path.append(path.join(path.dirname(sys.argv[0]), "../"))

tm_host = environ.get("TM_HOST") or "0.0.0.0"
# tm_port = environ.get("TM_PORT") or 6000
tm_port = 2017

monkey.patch_all(socket=False, thread=False)

if __name__ == "__main__":
    controller = Controller()
    # controller.deserialize()
    worker = Worker()
    server = zerorpc.Server(controller)
    server.bind("tcp://{ip}:{port}".format(ip=tm_host, port=tm_port))
    worker.register_callback("init_callback", controller.worker_init_callback)
    worker.register_callback("start_callback", controller.worker_start_callback)
    worker.register_callback("end_callback", controller.worker_end_callback)
    controller.register_callback("kill_callback", worker.kill_process_callback)
    gevent.joinall([gevent.spawn(server.run), gevent.spawn(worker.loop)])
