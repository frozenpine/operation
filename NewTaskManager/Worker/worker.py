# coding=utf-8
"""
Worker入口
"""

from NewTaskManager.protocol import Task
from external import ExternalSocketServer
from internal import InternalSocketServer
from msg_loop import msg_loop
from pool import worker_pool

if __name__ == '__main__':
    # 启动进程池
    worker_pool.start()
    # 启动内部通信用SocketServer
    internal_socket_server = InternalSocketServer('127.0.0.1', 7001)
    internal_socket_server.start()
    # 启动外部通信用SocketServer
    external_socket_server = ExternalSocketServer('0.0.0.0', 7002)
    external_socket_server.start()
    # 注册消息循环回调
    msg_loop.register_callback('task', worker_pool.run)
    msg_loop.register_callback('init', external_socket_server.send)
    msg_loop.register_callback('start', external_socket_server.send)
    msg_loop.register_callback('end', external_socket_server.send)
    # 启动消息循环
    msg_loop.start()
    # 初始化Task
    task = Task(queue_uuid='queue1',
                create_time='10:00',
                trigger_time='10:00',
                task_uuid='task1',
                task_info={
                    "remote": {
                        "params": {
                            "ip": "192.168.100.90",
                            "password": "qdam",
                            "user": "qdam"
                        },
                        "name": "SSHConfig"
                    },
                    "mod": {
                        "shell": "sleep 5",
                        "name": "shell"
                    }
                },
                task_earliest='10:00',
                task_latest='18:00',
                session='session')
    msg_loop.put('task', task)
