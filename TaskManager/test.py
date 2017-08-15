# coding=utf-8

import sys

import zerorpc
import zmq.green as zmq
from gevent import monkey

monkey.patch_all()
sys.modules["zmq"] = zmq

if __name__ == "__main__":
    # 阻塞 + 非阻塞
    task_dict = {
        "task_group1": {
            # 同步True, 异步False
            "group_block": True,
            "trigger_time": "20:00",
            "group_info": [
                {
                    "task_uuid": "task1",
                    "earliest": "12:30",
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
                            "shell": "exit 1",
                            "name": "shell"
                        }
                    }
                },
                {
                    "task_uuid": "task2",
                    "earliest": "",
                    "latest": "",
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
                },
                {
                    "task_uuid": "task3",
                    "earliest": "",
                    "latest": "",
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
        }
    }
    client = zerorpc.Client()
    client.connect("tcp://127.0.0.1:6000")
    client.init(task_dict, "2017-08-14")
    client.run_next("task_group1")
    # print client.update("task_group1", "task1",
    #                     {
    #                         "task_uuid": "task1",
    #                         "earliest": "",
    #                         "latest": "",
    #                         "detail": {
    #                             "remote": {
    #                                 "params": {
    #                                     "ip": "192.168.100.90",
    #                                     "password": "qdam",
    #                                     "user": "qdam"
    #                                 },
    #                                 "name": "SSHConfig"
    #                             },
    #                             "mod": {
    #                                 "shell": "sleep 8",
    #                                 "name": "shell"
    #                             }
    #                         }
    #                     })
    # client.run_next("task_group1")
