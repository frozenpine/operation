# coding=utf-8

import os

import zerorpc
import zmq
import zmq.auth


class ZeroClient(object):
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.public_keys_dir = os.path.join(self.base_dir, 'public_keys')
        self.secret_keys_dir = os.path.join(self.base_dir, 'private_keys')
        self.client_secret_file = os.path.join(self.secret_keys_dir, "client.key_secret")
        self.client_public, self.client_secret = zmq.auth.load_certificate(self.client_secret_file)
        self.server_public_file = os.path.join(self.public_keys_dir, "server.key")
        self.server_public, _ = zmq.auth.load_certificate(self.server_public_file)

    def init(self):
        ctx = zerorpc.Context.get_instance()
        cli = zerorpc.Client()
        zmq_socket = cli._events._socket
        zmq_socket.curve_secretkey = self.client_secret
        zmq_socket.curve_publickey = self.client_public
        zmq_socket.curve_serverkey = self.server_public
        return cli


if __name__ == "__main__":
    rpc_client = ZeroClient().init()
    rpc_client.connect('tcp://127.0.0.1:5555')
    print rpc_client.echo('foo')
