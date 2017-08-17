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
        },
        "task_group2": {
            # 同步True, 异步False
            "group_block": True,
            "trigger_time": "20:00",
            "group_info": [
                {
                    "task_uuid": "task4",
                    "earliest": "",
                    "latest": "",
                    "detail": {
                        "remote": {
                            "params": {
                                "ip": "192.168.101.163",
                                "user": "administrator",
                                "password": "Quantdo123456"
                            },
                            "name": "WinRmConfig"
                        },
                        "mod": {
                            "name": "wincpu"
                        }
                    }
                },
                {
                    "task_uuid": "task5",
                    "earliest": "",
                    "latest": "",
                    "detail": {
                        "remote": {
                            "params": {
                                "ip": "192.168.101.163",
                                "user": "administrator",
                                "password": "Quantdo123456"
                            },
                            "name": "WinRmConfig"
                        },
                        "mod": {
                            "name": "wincpu"
                        }
                    }
                },
                {
                    "task_uuid": "task6",
                    "earliest": "",
                    "latest": "",
                    "detail": {
                        "remote": {
                            "params": {
                                "ip": "192.168.101.163",
                                "user": "administrator",
                                "password": "Quantdo123456"
                            },
                            "name": "WinRmConfig"
                        },
                        "mod": {
                            "name": "wincpu"
                        }
                    }
                }
            ]
        },
    }
    client = zerorpc.Client()
    client.connect("tcp://127.0.0.1:6000")
    client.init(task_dict)
    client.run_next("task_group1")
    client.run_next("task_group2")
