# coding=utf-8

import sys

import zerorpc
import zmq.green as zmq
from gevent import monkey

monkey.patch_all()
sys.modules["zmq"] = zmq

if __name__ == "__main__":
    client = zerorpc.Client()
    client.connect("tcp://127.0.0.1:6000")
    # 同步队列
    task_dict = {
        "task_group1": {
            # 同步True, 异步False
            "group_block": True,
            "trigger_time": "",
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
            "trigger_time": "",
            "group_info": [
                {
                    "task_uuid": "task4",
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
                    "task_uuid": "task5",
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
                    "task_uuid": "task6",
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
    client.init(task_dict)
    # client.run_all("task_group1")
    # client.run_all("task_group2")
    # 异步队列
    # 单任务
    client.run_immediate(
        {
            "session": "session1",
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
                    "shell": "sleep 10",
                    "name": "shell"
                }
            }
        }
    )
    # 单任务
    client.run_immediate(
        {
            "session": "session2",
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
                    "shell": "sleep 10",
                    "name": "shell"
                }
            }
        }
    )
    # 任务组
    client.run_immediate(
        {"session": "session3",
         "task_info":
             [
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
                             "shell": "sleep 10",
                             "name": "shell"
                         }
                     }
                 },
                 {
                     "task_uuid": "task4",
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
                             "shell": "sleep 10",
                             "name": "shell"
                         }
                     }
                 }
             ]
         }
    )
