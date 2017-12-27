# coding=utf-8
"""
Worker入口
"""
import os
import sys
try:
    from msg_loop import MsgQueue
    from pool import worker_pool
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
    from msg_loop import MsgQueue
    from pool import worker_pool

# 初始化消息队列
msg_queue = MsgQueue()

if __name__ == '__main__':
    # 初始化消息循环
    from msg_loop import MsgLoop

    msg_loop = MsgLoop()

    # 启动内部通信用SocketServer
    from internal import InternalSocketServer

    internal_socket_server = InternalSocketServer('127.0.0.1', 7001)
    internal_socket_server.start()

    # 启动外部通信用SocketServer
    from external import ExternalSocketServer

    external_socket_server = ExternalSocketServer('127.0.0.1', 7000)
    external_socket_server.start()

    # 启动进程池
    worker_pool.start()

    # 注册消息循环回调
    msg_loop.register_callback('task', worker_pool.run)
    msg_loop.register_callback('init', external_socket_server.send)
    msg_loop.register_callback('start', external_socket_server.send)
    msg_loop.register_callback('end', external_socket_server.send)

    # 启动消息循环
    msg_loop.start()
    msg_loop.join()
