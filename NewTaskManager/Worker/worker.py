# coding=utf-8
"""
Worker入口
"""

from external import ExternalSocketServer
from internal import InternalSocketServer
from msg_loop import msg_loop
from pool import worker_pool

if __name__ == '__main__':
    worker_pool.start()
    internal_socket_server = InternalSocketServer('127.0.0.1', 7001)
    internal_socket_server.start()
    external_socket_server = ExternalSocketServer('0.0.0.0', 7002)
    external_socket_server.start()
    msg_loop.start()
    msg_loop.register_callback('task', worker_pool.run)
    msg_loop.register_callback('init', external_socket_server.send)
    msg_loop.register_callback('start', external_socket_server.send)
    msg_loop.register_callback('end', external_socket_server.send)
