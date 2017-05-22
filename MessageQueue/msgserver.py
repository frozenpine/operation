<<<<<<< HEAD
# coding=utf-8
from geventwebsocket import WebSocketError
from msgqueue import LogQueue
from flask import json

class MessageType:
    public = LogQueue
    Syslog = LogQueue

class MessageServer(object):
    def __init__(self, msg_type='public', sink_timmer=5):
        self.observers = []
        self.message_queue = getattr(MessageType, msg_type)(msg_type, sink_timmer)
=======
# -*- coding: UTF-8 -*-
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
>>>>>>> 4-qdiam-special
        self.message_queue.setDaemon(True)
        self.message_queue.start()

    def put_message(self, msg):
        self.message_queue.put(msg)
<<<<<<< HEAD
        self.send_message(msg)

    def send_message(self, msg):
        if self.observers:
            for ws in self.observers:
                try:
                    ws.send(msg)
                except WebSocketError:
                    self.observers.remove(ws)
                    continue

    def subscribe(self, websocket):
        try:
            self.observers.index(websocket)
        except ValueError:
            self.observers.append(websocket)
            return True
        else:
            return False

    def unsubscribe(self, websocket):
        try:
            self.observers.pop(self.observers.index(websocket))
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def parseRequest(websocket):
        receive = websocket.receive()
        try:
            msg = json.loads(receive)
        except ValueError:
            websocket.send(
                json.dumps({
                    'Message': """I didn't understand.""",
                    'Raw': receive
                })
            )
            return
        if 'subscribe' in msg.keys():
            topic = msg['subscribe']
            if MessageQueues.has_key(topic):
                if MessageQueues[topic].subscribe(websocket):
                    websocket.send(
                        json.dumps({
                            'Message': 'Topic "{}" subscribed successfully.'.format(topic)
                        })
                    )
                else:
                    websocket.send(
                        json.dumps({
                            'Message': 'Topic "{}" subscribed failed.'.format(topic)
                        })
                    )
            else:
                websocket.send(
                    json.dumps({
                        'Message': 'Topic "{}" not found.'.format(topic)
                    })
                )
            return
        if 'heartbeat' in msg.keys():
            websocket.send(
                json.dumps({
                    'Message': msg['heartbeat']
                })
            )
            return
        if 'unsubscribe' in msg.keys():
            topic = msg['unsubscribe']
            if MessageQueues.has_key(topic):
                if MessageQueues[topic].unsubscribe(websocket):
                    websocket.send(
                        json.dumps({
                            'Message': "Topic {} unsubscripbed successfully. "\
                                .format(topic)
                        })
                    )
                else:
                    websocket.send(
                        json.dumps({
                            'Message': "You haven't subscribe topic {} before."\
                                .format(topic)
                        })
                    )
            else:
                websocket.send(
                    json.dumps({
                        'Message': 'Topic "{}" not found.'.format(topic)
                    })
                )
            return
        websocket.send(
            json.dumps({
                'Message': """I didn't understand.""",
                'Raw': json.dumps(msg)
            })
        )
=======

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
                #print len(self.observers)
                #print self.observers
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
        #print msg
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
>>>>>>> 4-qdiam-special

MessageQueues = {
    'public': MessageServer('public')
}
