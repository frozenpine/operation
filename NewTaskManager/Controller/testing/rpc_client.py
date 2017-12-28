# coding=utf-8

from os import environ

from zerorpc import Client

if __name__ == '__main__':
    tm_host = environ.get('TM_HOST') or '127.0.0.1'
    tm_port = environ.get('TM_PORT') or 6000
    client = Client()
    client.connect("tcp://{ip}:{port}".format(ip=tm_host, port=tm_port))

    queue_id = '2266f7c4-95f2-4172-96ec-fb8e516aec1a'
    task1_id = 'd27d67d7-9c4f-428d-90df-a577a49f5b20'
    task2_id = '5ad839b3-3a7a-45a1-b6fa-1abb2fcc0510'
    task3_id = '306ef1a9-aeb1-4232-b4dc-9487cd3df55a'

    queue_dict = {
        queue_id: {
            'group_block': True,
            'trigger_time': '08:00',
            'group_info': [
                {
                    'task_uuid': task1_id,
                    'detail': {
                        "remote": {
                            "params": {
                                "ip": "192.168.100.90",
                                "password": "qdam",
                                "user": "qdam"
                            },
                            "name": "SSHConfig"
                        },
                        "mod": {
                            "shell": "echo hello",
                            "name": "shell"
                        }
                    },
                    'earliest': None,
                    'latest': None
                },
                {
                    'task_uuid': task2_id,
                    'detail': {
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
                    'earliest': None,
                    'latest': None
                },
                {
                    'task_uuid': task3_id,
                    'detail': {
                        "remote": {
                            "params": {
                                "ip": "192.168.100.90",
                                "password": "qdam",
                                "user": "qdam"
                            },
                            "name": "SSHConfig"
                        },
                        "mod": {
                            "shell": "echo done",
                            "name": "shell"
                        }
                    },
                    'earliest': None,
                    'latest': None
                }
            ]
        }
    }

    ''' try:
        force = True
        code, msg = client.init(queue_dict, force)
        print code, msg
        if force and code != 0:
            sys.exit()
    except Exception as err:
        print err
        client.close() '''
    # result = client.peek(queue_id, task3_id)
    # print result
    # result = client.peek(queue_id, task1_id)
    # print result
    # print client.run_next('123456')
    client.init(queue_dict, True)
    print client.snapshot('f59666ac-a336-452f-9665-aaa792f41d83', compatiable=False)
    print client.run_next(queue_id)
    print client.snapshot('f59666ac-a336-452f-9665-aaa792f41d83', compatiable=False)
    print client.run_all(queue_id)
    print client.snapshot('f59666ac-a336-452f-9665-aaa792f41d83', compatiable=False)
    client.close()
