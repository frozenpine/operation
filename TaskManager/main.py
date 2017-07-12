# coding=utf-8

import gevent
import zerorpc
from gevent import monkey

from controller import Controller
from worker import Worker


monkey.patch_all(socket=False, thread=False)

if __name__ == "__main__":
    controller = Controller()
    worker = Worker()
    server = zerorpc.Server(controller)
    server.bind("tcp://0.0.0.0:2017")
    worker.register_callback("start_callback", controller.worker_start_callback)
    worker.register_callback("end_callback", controller.worker_end_callback)
    gevent.joinall([gevent.spawn(server.run), gevent.spawn(worker.loop)])
