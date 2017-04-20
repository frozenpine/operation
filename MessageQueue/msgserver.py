# coding=utf-8
from geventwebsocket import WebSocketError
from msgqueue import LogQueue


class MessageServer(object):
    def __init__(self, topic):
        self.observers = []
        self.topic = topic
        self.message_queue = LogQueue(self.topic, 5)
        self.message_queue.setDaemon(True)
        self.message_queue.start()

    def put_message(self, msg):
        self.message_queue.put(msg)
        self.send_message(msg)

    def send_message(self, msg):
        if self.observers:
            for ws in self.observers:
                try:
                    ws.send(msg)
                except WebSocketError:
                    self.observers.pop(self.observers.index(ws))
                    continue

    def subscribe(self, websocket):
        self.observers.append(websocket)

    def unsubscribe(self, websocket):
        self.observers.pop(self.observers.index(websocket))
