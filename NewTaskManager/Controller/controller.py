# coding=utf-8

from multiprocessing import Queue

from controller_msg_loop import MsgLoop
from controller_socket import ControllerSocketServer

msg_queue = Queue()

if __name__ == '__main__':
    socket_server = ControllerSocketServer('127.0.0.1', 7000)
    socket_server.start()
    msg_loop = MsgLoop()
    msg_loop.start()
