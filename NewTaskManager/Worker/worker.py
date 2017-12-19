# coding=utf-8

from Queue import Queue

from worker_msg_loop import msg_loop
from worker_pool import worker_pool
from worker_socket import socket_server
from internal_socket import internal_server

msg_queue = Queue()

if __name__ == '__main__':
    internal_server.start()
    socket_server.start()
    msg_loop.start()
    worker_pool.start()
