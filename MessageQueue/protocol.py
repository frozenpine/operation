# -*- coding: UTF-8 -*-

class WebsocketProtocol(dict):
    version = '1.0'

    def __init__(self, **kwargs):
        super(WebsocketProtocol, self).__init__()
