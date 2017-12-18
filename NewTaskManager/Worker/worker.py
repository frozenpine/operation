# coding=utf-8

from Queue import Queue
from multiprocessing import Pool

from worker_msg_loop import MsgLoop
from worker_socket import WorkerSocketServer

msg_queue = Queue()

if __name__ == '__main__':
    socket_server = WorkerSocketServer('127.0.0.1', 7000)
    socket_server.start()
    msg_loop = MsgLoop()
    msg_loop.start()
    pool = Pool()
    pool.close()
    pool.join()
