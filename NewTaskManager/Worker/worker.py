# coding=utf-8
"""
Worker入口
"""
import os
import sys
from os import environ

try:
    from msg_loop import MsgQueue
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
    from msg_loop import MsgQueue

# 初始化消息队列
msg_queue = MsgQueue()

try:
    from pool import worker_pool
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
    from pool import worker_pool

if __name__ == '__main__':
    # 初始化消息循环
    from msg_loop import MsgLoop

    msg_loop = MsgLoop()

    # 启动内部通信用SocketServer
    from NewTaskManager.Common import get_port
    from internal import InternalSocketServer

    port = get_port.get_port()
    internal_socket_server = InternalSocketServer('127.0.0.1', port)
    internal_socket_server.start()

    # 启动外部通信用SocketServer
    from external import ExternalSocketServer

    controller_host = environ.get('CONTROLLER_HOST', '127.0.0.1')
    controller_port = int(environ.get('CONTROLLER_PORT', 7000))
    external_socket_server = ExternalSocketServer(controller_host, controller_port)
    external_socket_server.start()

    # 启动进程池
    worker_pool.start(port)

    # 注册消息循环回调
    msg_loop.register_callback('task', worker_pool.run)
    msg_loop.register_callback('except', external_socket_server.send)
    msg_loop.register_callback('init', external_socket_server.send)
    msg_loop.register_callback('hello', external_socket_server.send)
    msg_loop.register_callback('health_query', worker_pool.get_health)
    msg_loop.register_callback('health_callback', external_socket_server.send)
    msg_loop.register_callback('start', external_socket_server.send)
    msg_loop.register_callback('end', external_socket_server.send)

    # 启动消息循环
    msg_loop.start()
    msg_loop.join()
