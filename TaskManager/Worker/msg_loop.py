# coding=utf-8
"""
Worker内部消息循环
"""

import json
from Queue import Queue
from threading import Thread

from TaskManager.Worker import worker_logger as logging


class Event(object):
    def __init__(self, event_name, event_data):
        self.event_name = event_name
        self.event_data = event_data


class MsgQueue(Queue):
    def __init__(self):
        Queue.__init__(self)

    def put_event(self, event_name, event_data):
        self.put(Event(event_name, event_data))
        logging.info(u'MsgQueue Put EventName: {0}, EventData: {1}'.format(
            event_name, json.dumps(event_data.to_dict(), ensure_ascii=False)))


class MsgLoop(Thread):

    def __init__(self):
        super(MsgLoop, self).__init__()
        self.callback_dict = dict()

    def register_callback(self, event_name, callback_func):
        if event_name not in self.callback_dict:
            self.callback_dict.update({event_name: [callback_func]})
        else:
            self.callback_dict.get(event_name).append(callback_func)

    def unregister_callback(self, event_name, func):
        if event_name not in self.callback_dict:
            logging.warning(u'未找到该事件名称')
            return -1
        else:
            callback_list = self.callback_dict.get(event_name)
            if func not in callback_list:
                logging.warning(u'未注册该回调函数')
                return -1
            else:
                callback_list.remove(func)
                if not callback_list:
                    self.callback_dict.pop(event_name)

    def run(self):
        from TaskManager.Worker.worker import msg_queue
        logging.info('msg_loop')
        while 1:
            event = msg_queue.get()
            logging.info(u'MsgLoop Get EventName: {0}, EventData: {1}'.format(
                event.event_name, json.dumps(event.event_data.to_dict(), ensure_ascii=False)))
            event_name = event.event_name
            callback_list = self.callback_dict.get(event_name)
            for each in callback_list:
                each(event)
