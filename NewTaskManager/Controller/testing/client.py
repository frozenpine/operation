# coding=utf-8

import sys
from os import path, environ
from uuid import uuid4

sys.path.append(path.join(path.dirname(__file__), '../../../'))

from zerorpc import Client

if __name__ == '__main__':
    tm_host = environ.get('TM_HOST') or '127.0.0.1'
    tm_port = environ.get('TM_PORT') or 6000
    client = Client()
    client.connect("tcp://{ip}:{port}".format(ip=tm_host, port=tm_port))

    queue_id = str(uuid4())
    task1_id = str(uuid4())
    task2_id = str(uuid4())
    task3_id = str(uuid4())

    queue_dict = {
        queue_id: {
            'group_block': True,
            'trigger_time': '08:00',
            'group_info': [
                {
                    'task_uuid': task1_id,
                    'detail': {},
                    'earliest': None,
                    'latest': None
                },
                {
                    'task_uuid': task2_id,
                    'detail': {},
                    'earliest': None,
                    'latest': None
                },
                {
                    'task_uuid': task3_id,
                    'detail': {},
                    'earliest': None,
                    'latest': None
                }
            ]
        }
    }

    client.init(queue_dict, True)

    result = client.peak(queue_id, task3_id)
    print result

    result = client.peek(queue_id, task1_id)
    print result