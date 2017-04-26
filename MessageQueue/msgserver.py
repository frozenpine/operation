# coding=utf-8
from geventwebsocket import WebSocketError
from msgsink import LogSinker
import json
import time

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

class MessageServer(object):
    switchRequest = {
        'subscribe': lambda req: req_subscribe(req),
        'unsubscribe': lambda req: req_unsubscribe(req),
        'heartbeat': lambda req: req_heartbeat(req)
    }
    def __init__(self, topic):
        self.observers = set()
        self.topic = topic
        self.message_queue = LogSinker(self.topic, 5)
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
                print len(self.observers)
                print self.observers
                fail_socket.add(ws)
                continue
        self.observers -= fail_socket

    def subscribe(self, websocket):
        self.observers.add(websocket)

    def unsubscribe(self, websocket):
        self.observers.remove(websocket)

    @staticmethod
    def parse_request(websocket):
        msg = websocket.receive()
        print msg
        try:
            request = json.loads(msg)
        except ValueError:
            websocket.send(json.dumps({
                'error': """Sorry, i don't understand."""
            }))
        else:
            request['ws'] = websocket
            try:
                MessageServer.switchRequest[request['method']](request)
            except KeyError:
                websocket.send(json.dumps({
                    'error': """Request method not valid."""
                }))

MessageQueues = {
    'public': MessageServer('public')
}
