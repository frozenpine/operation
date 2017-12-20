# coding=utf-8


import socket

from NewTaskManager.protocol import Task
from NewTaskManager.protocol import TmProtocol

if __name__ == '__main__':
    payload = Task(
        queue_uuid='queue1',
        create_time='00:00',
        trigger_time='00:00',
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
        task_earliest='02:00',
        task_latest='22:00',
        session='session'
    )
    tm_protocol = TmProtocol('test_client', 'external_server', payload)
    buff = tm_protocol.serial()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 7002))
    s.send(buff)
