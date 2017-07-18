# -*- coding: UTF-8 -*-
import json
import time

from geventwebsocket import WebSocketError

from msgsink import LogSinker, JSONSinker


def req_subscribe(request):
    try:
        topic = request['topic']
    except KeyError:
        request['ws'].send(json.dumps({
            'error': 'Missing topic.'
        }))
    else:
        if MessageQueues.has_key(topic):
            MessageQueues[topic].subscribe(request['ws'])
            request['ws'].send(json.dumps({
                'message': 'Topic {} subscribed successfully.'.format(topic)
            }))
        else:
            request['ws'].send(json.dumps({
                'error': 'Topic {} not exist.'.format(topic)
            }))

def req_unsubscribe(request):
    try:
        topic = request['topic']
    except KeyError:
        request['ws'].send(json.dumps({
            'error': 'Missing topic.'
        }))
    else:
        if MessageQueues.has_key(topic):
            try:
                MessageQueues[topic].unsubscribe(request['ws'])
            except KeyError:
                request['ws'].send(json.dumps({
                    'error': """You haven't subscribed this topic[{}]""".format(topic)
                }))
            else:
                request['ws'].send('Topic {} unsubscribed successfully.').format(topic)
        else:
            request['ws'].send(json.dumps({
                'error': 'Topic {} not exist.'.format(topic)
            }))

def req_heartbeat(request):
    request['ws'].send(json.dumps({
        'heartbeat': time.strftime('%Y-%m-%d %H:%M:%S')
    }))

def req_topics(request):
    request['ws'].send(json.dumps({
        'topics': MessageQueues.keys()
    }))

class MessageServer(object):
    def __init__(self, topic, sinker):
        self.observers = set()
        self.topic = topic
        self.message_queue = sinker
        self.message_queue.setDaemon(True)
        self.message_queue.start()

    def put_message(self, msg):
        self.message_queue.put(msg)

    def send_message(self, msg):
        self.put_message(msg)
        fail_socket = set()
        for ws in self.observers:
            try:
                ws.send(json.dumps({
                    'topic': self.topic,
                    'data': msg
                }))
            except WebSocketError:
                fail_socket.add(ws)
                continue
        self.observers -= fail_socket

    def send_object(self, obj):
        self.send_message(json.dumps(obj))

    def subscribe(self, websocket):
        self.observers.add(websocket)

    def unsubscribe(self, websocket):
        self.observers.remove(websocket)

    @staticmethod
    def parse_request(websocket):
        msg = websocket.receive()
        try:
            request = json.loads(msg)
        except ValueError:
            websocket.send(json.dumps({
                'error': "Sorry, i don't understand."
            }))
        else:
            request['ws'] = websocket
            try:
                method = request['method']
                globals()['req_{}'.format(method)](request)
            except KeyError:
                websocket.send(json.dumps({
                    'error': 'Request method not valid.'
                }))

MessageQueues = {
    'public': MessageServer('public', LogSinker('public')),
    'tasks': MessageServer('tasks', JSONSinker('tasks', 10))
}
