# coding=utf-8
"""
任务调度器
"""

# import random
import socket
import threading
from Queue import PriorityQueue
from SocketServer import StreamRequestHandler, TCPServer, ThreadingMixIn
import os
import ssl
from TaskManager.Controller import controller_logger as logging
from TaskManager.Controller.events import EventName
from TaskManager.excepts import DeserialError
from TaskManager.protocol import (MSG_DICT, Health, Hello, MessageType, Goodbye,
                                  TaskResult, TaskStatus, TmProtocol)


class ThreadedTCPRequestHandler(StreamRequestHandler):
    """
    SocketServer 每连接处理线程
    """
    def _process(self, data):
        worker_name = data.source
        payload = data.payload
        if isinstance(payload, Hello):
            self.server.add_worker(data.source, self.request)
            logging.info('Client[{}]{} say hello.'.format(worker_name, self.client_address))
        if isinstance(payload, Goodbye):
            self.server.del_worker(worker_name)
            logging.info('Client[{}]{} say goodbye.'.format(worker_name, self.client_address))
        if isinstance(payload, Health):
            # todo: 更改Health字段
            priority = 60 * payload.process_load + 20 * payload.cpu_load + 20 * payload.mem_load
            # self.server.free_worker(random.randint(1, 100), worker_name)
            self.server.free_worker(priority, worker_name)
            logging.info('Client[{}]{} health: (cpu_use: {:.2%}, mem_use: {:.2%}, worker_use: {:.2%})'.format(
                worker_name, self.client_address, payload.cpu_load, payload.mem_load, payload.process_load))
        if isinstance(payload, TaskResult):
            self.server.send_result(payload)
            logging.info('Client[{}]{} report task result: {}'.format(
                worker_name, self.client_address, payload.to_dict()))
            ''' if payload.status_code.IsDone:
                self.server.free_worker(random.randint(1, 100), worker_name) '''

    def handle(self):
        while True:
            try:
                buff = self.request.recv(8192)
            except socket.error:
                logging.warning('Client disconnect: {0}'.format(self.client_address))
                break
            if buff:
                try:
                    data = TmProtocol.deserial(buff)
                except (DeserialError, ValueError) as err:
                    logging.warning('Protocol format error: {0}'.format(err.message))
                else:
                    self._process(data)
            else:
                break


def locker(func):
    """ 线程锁装饰器 """
    def wrapper(self, *args, **kwargs):
        self._condition.acquire()
        try:
            return func(self, *args, **kwargs)
        finally:
            self._condition.release()

    wrapper.__doc__ = func.__doc__
    return wrapper


class TaskDispatcher(ThreadingMixIn, TCPServer, threading.Thread):
    def __init__(self, svr_addr, svr_port, event_global,
                 request_handler=ThreadedTCPRequestHandler, bind_and_active=True):
        threading.Thread.__init__(self)
        TCPServer.__init__(self, (svr_addr, svr_port), request_handler, bind_and_active)
        self._worker_cache = {}
        self._event_queue = event_global
        self._worker_arb = PriorityQueue()
        self._server_cert = os.path.join(os.path.dirname(__file__), os.pardir, 'SSLCerts', 'server.crt')
        self._server_key = os.path.join(os.path.dirname(__file__), os.pardir, 'SSLCerts', 'server.key')
        self._ca_certs = os.path.join(os.path.dirname(__file__), os.pardir, 'SSLCerts', 'ca.crt')
        self._condition = threading.Condition(threading.RLock())

    def run(self):
        self.serve_forever()

    def get_request(self):
        new_socket, from_address = self.socket.accept()
        conn_stream = ssl.wrap_socket(
            new_socket, server_side=True, certfile=self._server_cert, keyfile=self._server_key,
            ca_certs=self._ca_certs, ssl_version=ssl.PROTOCOL_TLSv1_2)
        return conn_stream, from_address

    @locker
    def wait_for_worker(self, timeout=None):
        if not self._worker_cache:
            self._condition.wait(timeout)

    @locker
    def has_worker(self):
        if self._worker_cache:
            return True
        else:
            return False

    @locker
    def add_worker(self, name, request):
        if name in self._worker_cache:
            self._worker_cache[name].close()
            del self._worker_cache[name]
        self._worker_cache[name] = request
        self._condition.notifyAll()

    @locker
    def del_worker(self, name):
        try:
            request = self._worker_cache.pop(name)
        except KeyError:
            msg = 'Worker[{}] already disconnected'.format(name)
            logging.warning(msg)
        else:
            request.close()
            self._condition.notifyAll()

    @locker
    def worker_exists(self, name):
        return name in self._worker_cache

    @locker
    def get_worker(self, name):
        try:
            return self._worker_cache[name]
        except KeyError:
            msg = 'Worker[{}] already disconnected'.format(name)
            logging.warning(msg)
            raise Exception(msg)

    def free_worker(self, priority, name):
        self._worker_arb.put((priority, name))

    def worker_arb(self):
        priority, name = self._worker_arb.get()
        logging.info('Current worker: {}[{}]'.format(name, priority))
        return name

    def send_task(self, name, task):
        while True:
            try:
                worker = self.get_worker(name)
                worker.sendall(
                    TmProtocol(src='MASTER', dest=name, payload=task, msg_type=MessageType.Private).serial())
            except Exception as err:
                logging.warning(err)
                self.wait_for_worker()
                name = self.worker_arb()
            else:
                break

    def send_result(self, task_result):
        self._event_queue.put_event(EventName.TaskResult, task_result)

    # def task_dispatcher(self, event):
    def event_relay(self, event):
        """
        任务分发器，由外部callback触发
        """
        if event.Name == EventName.TaskDispatch:
            worker_name = self.worker_arb()
            task = event.Data
            self.send_task(worker_name, task)
            logging.info('Task[{}] assigned to worker[{}]'.format(event.Data.task_uuid, worker_name))
            self.send_result(TaskResult(
                task.queue_uuid, task.task_uuid, TaskStatus.Dispatched,
                MSG_DICT[TaskStatus.Dispatched], task.session))
        else:
            logging.warning('Invalid event[{}] routed'.format(event.Name))


'''
class TaskDispatcher(threading.Thread):
    def __init__(self, host, port, event_queue):
        threading.Thread.__init__(self)
        self._event_global = event_queue
        # self._event_local = Queue()
        # self._callback_cache = {}

        self._worker_manager = ThreadedTCPServer(self._event_global, (host, port), ThreadedTCPRequestHandler)

        # self._event_handler = threading.Thread(
        #     target=self._event_dispatcher, args=(self._event_local, self._callback_cache, self._worker_manager))
        # self._event_handler.setDaemon(True)
        # self._event_handler.start()

        self._register_callback(EventName.TaskDispatch, self._worker_manager.task_dispatcher)

    def run(self):
        self._worker_manager.serve_forever()

    # this func called by outside message loop
    def event_relay(self, event):
        logging.info('Event received: {} {}'.format(event.Name, event.Data.to_dict()))
        self._event_local.put_nowait(event)

    def _register_callback(self, event_name, callback):
        if event_name not in self._callback_cache:
            self._callback_cache[event_name] = [callback]
        else:
            self._callback_cache[event_name].append(callback)

    def _unregister_callback(self, event_name, callback):
        if event_name not in self._callback_cache:
            logging.warning(u'未找到该事件名称')
            return False
        else:
            callback_list = self._callback_cache[event_name]
            if callback not in callback_list:
                logging.warning(u'未注册该回调函数')
                return False
            else:
                callback_list.remove(callback)
                if not callback_list:
                    self._callback_cache.pop(event_name)

    @staticmethod
    def _event_dispatcher(event_local, callback_cache, worker_manager):
        worker_manager.wait_for_worker()
        while True:
            event = event_local.get()
            if event.Name not in callback_cache:
                logging.warning('No callback registed on this event[{}]: {}'.format(event.Name, event.Data.to_dict()))
            else:
                for func in callback_cache[event.Name]:
                    func(event)
'''
