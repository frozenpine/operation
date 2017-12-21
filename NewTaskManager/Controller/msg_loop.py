# coding=utf-8
"""
Controller内部消息循环
"""

from multiprocessing.queues import Queue
# from Queue import Queue
# from gevent.queue import Queue
from threading import Thread

from NewTaskManager.Controller import controller_logger as logging
from NewTaskManager.Controller.events import MessageEvent


class MsgQueue(Queue):
    def __init__(self, *args, **kwargs):
        Queue.__init__(self, *args, **kwargs)

    def put_event(self, event_name, event_data):
        self.put(MessageEvent(event_name, event_data))
        # logging.info('MsgQueue Put EventName: {0} EventData: {1}'.format(event_name, event_data.to_dict()))


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
        from NewTaskManager.Controller.controller import msg_queue
        logging.info('Message loop started')
        while True:
            event = msg_queue.get()
            # logging.info('MsgLoop Get EventName: {0} EventData: {1}'.format(event.Name, event.Data.to_dict()))
            callback_list = self.callback_dict.get(event.Name)
            for each in callback_list:
                each(event)
