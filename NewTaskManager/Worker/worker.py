# coding=utf-8

from Queue import Queue

from worker_msg_loop import msg_loop
from worker_pool import worker_pool
from worker_socket import socket_server

msg_queue = Queue()

if __name__ == '__main__':
    socket_server.start()
    msg_loop.start()
    worker_pool.start()
