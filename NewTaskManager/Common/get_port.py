# coding=utf-8

import random
import socket


def is_close(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return False
    except Exception, e:
        return True


def get_port():
    while 1:
        port = 7000 + random.randint(1, 1000)
        ret = is_close('127.0.0.1', port)
        if ret:
            break
    return port
