# coding=utf-8

import sys
import time

import zerorpc
import zmq.green as zmq
from gevent import monkey

monkey.patch_all()
sys.modules["zmq"] = zmq

if __name__ == "__main__":
    # 阻塞
    task_dict = {
        "task_group1": {
            "group_block": True,
            "group_info": [
                {
                    "task_uuid": "task1",
                    "earliest": "14:00",
                    "latest": "16:00",
                    "detail": {
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
                    }
                }
            ]
        },
        "task_group2": {
            "group_block": True,
            "group_info": [
                {
                    "task_uuid": "task6",
                    "earliest": "16:00",
                    "latest": "18:00",
                    "detail": {
                        "remote": {
                            "params": {
                                "ip": "192.168.100.90",
                                "password": "qdam",
                                "user": "qdam"
                            },
                            "name": "SSHConfig"
                        },
                        "mod": {
                            "shell": "slep 5",
                            "name": "shell"
                        }
                    }
                }
            ]
        }
    }
    client = zerorpc.Client()
    client.connect("tcp://127.0.0.1:2017")
    # print client.deserialize()
    print client.init(task_dict)
    # print client.run_next("task_group1")
    print client.run_next("task_group2")
    time.sleep(3)
    print client.resume("task_group2")
