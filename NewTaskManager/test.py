# coding=utf-8

import time

import requests

if __name__ == '__main__':
    count = 0
    while 1:
        count += 1
        print count
        r = requests.post('http://127.0.0.1:6001/api/op_group/id/1')
        r = requests.get('http://127.0.0.1:6001/api/op_group/id/1/all')
        time.sleep(20)
