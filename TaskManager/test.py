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
            "group_block": True,
            "group_info": [
                {
                    "task_uuid": "task1",
                    "earliest": "9:20",
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
            "group_block": True,
            "group_info": [
                {
                    "task_uuid": "task6",
                    "earliest": "13:00",
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
                            "shell": "sleep 5",
                            "name": "shell"
                        }
                    }
                },
                {
                    "task_uuid": "task7",
                    "earliest": "13:00",
                    "latest": "20:00",
                    "detail": {
                        "remote": {
                            "params": {
                                "ip": "192.168.100.90",
                                "password": "qdam1",
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
                    "task_uuid": "task8",
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
    print client.init(task_dict, True)
    print client.run_all("task_group1")
