# coding=utf-8

import os

import zerorpc
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator


class Controller(object):

    def echo(self, msg):
        return msg


class ZeroServer(object):
    def __init__(self, methods, whitelist=None):
        self.methods = methods
        if not whitelist:
            self.whitelist = ['127.0.0.1']
        else:
            self.whitelist = whitelist
        self.base_dir = os.path.dirname(__file__)
        self.public_keys_dir = os.path.join(self.base_dir, 'public_keys')
        self.secret_keys_dir = os.path.join(self.base_dir, 'private_keys')
        self.server_secret_file = os.path.join(self.secret_keys_dir, "server.key_secret")
        self.server_public, self.server_secret = zmq.auth.load_certificate(self.server_secret_file)

    def init(self):
        srv = zerorpc.Server(self.methods)
        ctx = zerorpc.Context.get_instance()
        auth = ThreadAuthenticator(ctx)
        auth.start()
        auth.allow(*self.whitelist)
        auth.configure_curve(domain='*', location=self.public_keys_dir)
        zmq_socket = srv._events._socket
        zmq_socket.curve_secretkey = self.server_secret
        zmq_socket.curve_publickey = self.server_public
        zmq_socket.curve_server = True
        return srv


if __name__ == "__main__":
    server = ZeroServer(Controller()).init()
    server.bind('tcp://127.0.0.1:5555')
    server.run()
