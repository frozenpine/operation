# coding=utf-8

from SocketServer import StreamRequestHandler, ThreadingMixIn, TCPServer
import threading
import random

from Queue import Queue, PriorityQueue

from NewTaskManager.protocol import TmProtocol, TaskResult, TaskStatus, MSG_DICT, Heartbeat, MessageType, Hello
from NewTaskManager.excepts import DeserialError
from NewTaskManager.Controller import controller_logger as logging
from NewTaskManager.Controller.events import EventName, MessageEvent


class ThreadedTCPRequestHandler(StreamRequestHandler):
    def _process(self, data):
        if not self.server.worker_exists(data.source):
            self.server.add_worker(data.source, self.request)
        worker_name = data.source
        payload = data.payload
        if isinstance(payload, TaskResult):
            self.server.send_result(payload)
        if isinstance(payload, Heartbeat):
            self.server.heartbeat_countup(worker_name)
            self.request.send(
                TmProtocol(src='MASTER', dest=worker_name, payload=Heartbeat(), msg_type=MessageType.Private).serial())
            logging.info('Heartbeat from client: {}'.format(self.client_address))
        if isinstance(payload, Hello):
            self.server.free_worker(worker_name, random.randint(1, 100))
            logging.info('Client {} say hello.'.format(self.client_address))
        return True

    def handle(self):
        while True:
            try:
                buff = self.request.recv(8192)
            except:
                logging.warning('[socket] disconnect: {0}'.format(self.client_address))
                break
            try:
                data = TmProtocol.deserial(buff)
            except DeserialError as err:
                logging.warning('[socket] format error: {0}'.format(err.message))
            else:
                if not self._process(data):
                    break


def locker(func):
    def wrapper(self, *args, **kwargs):
        self._condition.acquire()
        try:
            return func(self, *args, **kwargs)
        finally:
            self._condition.release()
    wrapper.__doc__ = func.__doc__
    return wrapper


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    def __init__(self, result_cache, server_addr, request_handler, bind_and_active=True):
        TCPServer.__init__(self, server_addr, request_handler, bind_and_active)
        self._worker_cache = {}
        self._result_cache = result_cache
        self._worker_arb = PriorityQueue()
        self._heartbeat_cache = Queue()
        self._heartbeat_countdown = {}
        self._condition = threading.Condition(threading.RLock())

    @staticmethod
    def _heartbeat_timer(server, name):
        if server.heartbeat_countdown(name):
            timer = threading.Timer(5, ThreadedTCPServer._heartbeat_timer, [server, name])
            timer.setDaemon(True)
            timer.start()
        else:
            server.del_worker(name)

    @locker
    def heartbeat_countup(self, name):
        current_count = self._heartbeat_countdown[name]
        if current_count <= 3:
            self._heartbeat_countdown[name] = (current_count + 1)
        return self._heartbeat_countdown[name]

    def heartbeat_countdown(self, name):
        current_count = self._heartbeat_countdown[name]
        if current_count > 0:
            self._heartbeat_countdown[name] = (current_count - 1)
        return self._heartbeat_countdown[name]

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
        self._worker_cache[name] = request
        self._condition.notifyAll()
        self._heartbeat_countdown[name] = 3
        timmer = threading.Timer(5, ThreadedTCPServer._heartbeat_timer, [self, name])
        timmer.setDaemon(True)
        timmer.start()

    @locker
    def del_worker(self, name):
        try:
            request = self._worker_cache.pop(name)
        except KeyError:
            msg = 'Worker[{}] already disconnected'.format(name)
            logging.warning(msg)
        else:
            request.close()

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

    def free_worker(self, name, priority):
        self._worker_arb.put((priority, name))

    def worker_arb(self):
        priority, name = self._worker_arb.get()
        return name

    @locker
    def send_task(self, name, task):
        self._worker_cache[name].send(
            TmProtocol(src='MASTER', dest=name, payload=task, msg_type=MessageType.Private).serial())

    def send_result(self, task_result):
        self._result_cache.put_nowait(MessageEvent(EventName.TaskResult, task_result))


class TaskDispatcher(threading.Thread):
    def __init__(self, host, port, event_queue):
        threading.Thread.__init__(self)
        self._event_queue = event_queue
        self._task_cache = Queue()
        self._server = ThreadedTCPServer(event_queue, (host, port), ThreadedTCPRequestHandler)
        self._task_handler = threading.Thread(
            target=TaskDispatcher._dispatcher,
            args=(self._task_cache, self._server)
        )
        self._task_handler.setDaemon(True)
        self._task_handler.start()

    def run(self):
        self._server.serve_forever()

    def task_dispatch_callback(self, event):
        logging.info('Event received: {} {}'.format(event.Name, event.Data.to_dict()))
        self._task_cache.put_nowait(event.Data)

    @staticmethod
    def _dispatcher(task_cache, worker_cache):
        while True:
            worker_cache.wait_for_worker()
            task = task_cache.get()
            worker_name = worker_cache.worker_arb()
            worker_cache.send_task(worker_name, task)
