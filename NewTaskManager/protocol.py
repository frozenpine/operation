# coding=utf-8
"""
Protocol definition used between TaskManager's Master Node and Work Node.
"""

import hashlib
import json
import pickle
import time
from abc import ABCMeta, abstractmethod
from os import path

import yaml
from enum import Enum

from NewTaskManager import tm_logger
from NewTaskManager.excepts import DeserialError, InitialError
from SysManager.configs import Result


class MessageType(Enum):
    Broadcast = 0
    Private = 1


class PayloadType(Enum):
    Hello = 0
    Goodbye = 1
    Authentication = 10
    Confirmation = 20
    Health = 30
    Task = 40
    TaskResult = 50


class QueueStatus(Enum):
    Initiating = -2  # 正在初始化
    InitFailed = -1  # 初始化失败
    Empty = -11  # 队列为空
    NotExits = -12  # 队列不存在
    NotRecoverable = -13  # 失败不可恢复
    Expired = -14  # 队列已过期
    Normal = 0  # 正常调度
    Done = 10  # 队列已完成
    JobIssued = 11  # 任务已下发
    JobDispatched = 12  # 任务已调度
    JobRunning = 13  # 任务执行中
    JobWaiting = 14  # 任务等待中
    JobFailed = 15  # 任务失败

    @property
    def Dispatchable(self):
        return self == QueueStatus.Normal

    @property
    def Blocking(self):
        return self in [QueueStatus.JobIssued, QueueStatus.JobDispatched, QueueStatus.JobWaiting]

    @property
    def Recoverable(self):
        return self == QueueStatus.JobFailed


class TaskStatus(Enum):
    UnKnown = -100  # 未知错误
    Dispatched = -2  # 任务已由调度器调度
    InitFailed = -1  # 初始化失败
    Runnable = 100  # 可以直接执行
    TriggerTimeWaiting = 111  # 等待时间
    WorkerWaiting = 112  # 等待进程池
    TimeRangeExcept = 121  # 超出时间限制
    Running = 200  # 开始执行
    Success = 0  # 执行成功
    Failed = 1  # 执行失败
    Timeout = 2  # 自带超时
    Terminated = 3  # 强制终止
    Skipped = 4  # 跳过

    @property
    def IsExcepted(self):
        return self in [TaskStatus.UnKnown, TaskStatus.InitFailed, TaskStatus.TimeRangeExcept]

    @property
    def IsInited(self):
        return self in [TaskStatus.Runnable] or self.IsWaiting

    @property
    def IsWaiting(self):
        return self in [TaskStatus.TriggerTimeWaiting, TaskStatus.WorkerWaiting]

    @property
    def IsRunning(self):
        return self in [TaskStatus.Running]

    @property
    def IsDone(self):
        return self in [TaskStatus.Success, TaskStatus.Failed] or self.IsTimeout

    @property
    def IsTimeout(self):
        return self in [TaskStatus.Timeout, TaskStatus.Terminated]


MSG_DICT = {
    QueueStatus.Initiating: u'队列正在初始化',
    QueueStatus.InitFailed: u'初始化失败',
    QueueStatus.Empty: u'队列为空',
    QueueStatus.NotExits: u'队列不存在',
    QueueStatus.NotRecoverable: u'队列不可恢复',
    QueueStatus.Expired: u'队列已过期',
    QueueStatus.Normal: u'正常调度',
    QueueStatus.Done: u'队列已完成',
    QueueStatus.JobIssued: u'任务已下发',
    QueueStatus.JobDispatched: u'任务已调度',
    QueueStatus.JobRunning: u'任务执行中',
    QueueStatus.JobWaiting: u'任务等待中',
    QueueStatus.JobFailed: u'任务失败',
    TaskStatus.UnKnown: u'任务状态未知',
    TaskStatus.Dispatched: u'任务已调度',
    TaskStatus.InitFailed: u'初始化失败',
    TaskStatus.Runnable: u'可以直接执行',
    TaskStatus.TriggerTimeWaiting: u'等待触发时间',
    TaskStatus.WorkerWaiting: u'等待进程池',
    TaskStatus.TimeRangeExcept: u'超出时间限制',
    TaskStatus.Running: u'开始执行',
    TaskStatus.Success: u'执行成功',
    TaskStatus.Failed: u'执行失败',
    TaskStatus.Timeout: u'任务超时',
    TaskStatus.Terminated: u'强制终止',
    TaskStatus.Skipped: u'跳过'
}


class JsonSerializable(object):
    """ A json serialiable base class
    """

    __metaclass__ = ABCMeta
    __exclude__ = []

    def to_dict(self):
        """ Used to get  JSON data.

        Args: None

        Returns:
            JSON data w/o attributes in self.__exclude__ list.

        Raises:
            TypeError: An error occour when attribute not JSON serializable.
        """
        results = {}
        for field in [x for x in dir(self) if not x.startswith('_') and x not in self.__exclude__]:
            obj = getattr(self, field)
            if not callable(obj):
                if isinstance(obj, JsonSerializable):
                    results[field] = obj.to_dict()
                elif isinstance(obj, Result):
                    results[field] = obj.to_dict()
                elif isinstance(obj, Enum):
                    results[field] = obj.value
                elif isinstance(obj, list) or isinstance(obj, tuple):
                    results[field] = [x.to_dict() if isinstance(x, JsonSerializable) else x for x in obj]
                else:
                    results[field] = obj
        results.update({'_class_name': self.__class__.__name__.split('.')[-1]})
        return results

    @staticmethod
    @abstractmethod
    def from_dict(dict_data):
        """ An abstract method define, used to convert particular json to class instance
        """
        pass

    def serial(self, is_json=True):
        """ Used to serial object instance
        Args: None

        Returns: Serialized object instance
        """
        if is_json:
            return json.dumps(self, cls=JsonSerializableEncoder)
        else:
            return pickle.dumps(self)

    @classmethod
    def deserial(cls, buff, is_json=True):
        """ Used to deserial protocol message from str buffer
        Args:
            buff: pickle serialized buff string.

        Returns: Instance of class.

        Raises:
            DeserialError: An error occured when deserialized instance is not type of cls
        """
        if is_json:
            json_data = json.loads(buff)
            if '_class_name' in json_data:
                instance = globals()[json_data['_class_name']].from_dict(json_data)
            else:
                instance = json_data
        else:
            instance = pickle.loads(buff)
        if not isinstance(instance, cls):
            raise DeserialError('Deserialized instance not match class.')
        return instance

    def dump_file(self, dump_file):
        """ Dump class to YAML file

        Args:
            dump_file: A dump file path, either directory path or file path is fine
                if dump_file is a directory, YAML saved in name 'TmProtocol' and '_%Y%m%d%H%M%S' in time format.
                if dump_file is a file path and file exists, YAML saved with file name and
                '_%Y%m%d%H%M%S' in time format, old file will not be overwrited.
                if dump_file is a file path and file not exists, YAML saved in this particular dump file.

        Returns: None

        Raises:
            IOError: An error occour when dump file path invalid.
            TypeError: An error occour when attribute not JSON serializable.
        """
        if path.isdir(dump_file):
            directory = dump_file
            file_name = '{name}_{timestamp}.yaml'.format(
                name=self.__class__.__name__, timestamp=time.strftime('%Y%m%d%H%M%S'))
        else:
            directory = path.dirname(dump_file)
            if path.isdir(directory):
                # if path.isfile(dump_file):
                #     file_name = '{file_name}_{timestamp}.yaml'.format(
                #         file_name=path.basename(dump_file).split('.')[0],
                #         timestamp=time.strftime('%Y%m%d%H%M%S'))
                # else:
                #     file_name = path.basename(dump_file)
                file_name = path.basename(dump_file)
            else:
                message = '"{}" is neither an dir nor a regular file.'.format(dump_file)
                tm_logger.error(message)
                raise IOError(message)
        with open('{dir}/{file}'.format(dir=directory, file=file_name), mode='wb') as out_file:
            # message = 'Data is dumped into yaml file({dir}/{file})'.format(dir=directory, file=file_name)
            yaml.safe_dump(self.to_dict(), out_file, default_flow_style=False, allow_unicode=True)


class JsonSerializableEncoder(json.JSONEncoder):
    """ An json dumps encoder 4 JsonSerializable Class
    """

    def default(self, obj):
        if isinstance(obj, JsonSerializable):
            return obj.to_dict()
        else:
            return json.JSONEncoder.default(self, obj)


class TmProtocol(JsonSerializable):
    """
    Attributes:
        version: An version dict in major, minor & revision keys.
        source: Protocol message sender's name.
        destination: Protocol message receiver's name, defaults to 'public' when message_type is Broadcast.
        payload: Protocol message's data body.
        check_sum: Protocol message's md5 hash without check_sum itself.
    """

    version = {
        'major': 1,
        'minor': 0,
        'revision': 0
    }

    def __init__(self, src, dest, payload, msg_type=MessageType.Broadcast):
        """
        Args:
            src: Message sender's name.
            dest: Message receiver's name.
            payload: The real message data.
            msg_type: Message type, defaults to MessageType.Broadcast

        Returns: None

        Raises:
            InitialError: An error occured missing args
        """

        self.source = src
        self.destination = dest
        self.message_type = msg_type
        if self.message_type == MessageType.Broadcast:
            self.destination = 'public'
        try:
            type_name = payload.__class__.__name__.split('.')[-1]
            payload_type = PayloadType[type_name]
        except KeyError:
            raise InitialError('Invalid payload type "{}".'.format(type_name))
        self.payload_type = payload_type
        self.payload = payload
        self.__exclude__.append('check_sum')
        hasher = hashlib.md5(json.dumps(self, cls=JsonSerializableEncoder, sort_keys=True))
        self.check_sum = hasher.hexdigest()

    @staticmethod
    def from_dict(dict_data):
        """ Create an class instance from dict
        Args:
            dict_data: An dict object with specified key/value pairs
                Example: {
                    'source': 'some source',
                    'destination: 'some destination',
                    'message_type': 'MessageType Name',
                    'payload': 'Payload dict'
                }

        Returns: An instance of TmProtocol class

        Raises:
            KeyError: An error occour validating key/value pair.
        """
        src = dict_data['source']
        dest = dict_data['destination']
        msg_type = MessageType(dict_data['message_type'])
        try:
            payload_type = PayloadType(dict_data['payload_type'])
        except KeyError:
            raise DeserialError('Invlaid payload type "{}".'.format(dict_data['payload_type']))
        payload = globals()[payload_type.name].from_dict(dict_data['payload'])

        return TmProtocol(src=src, dest=dest, payload=payload, msg_type=msg_type)

    def is_valid(self):
        """ Verifing protocol message is valid
        Args: None

        Returns: Ture 4 data is valid, False 4 data is invalid.
        """
        hasher = hashlib.md5(json.dumps(self, cls=JsonSerializableEncoder, sort_keys=True))
        return hasher.hexdigest() == self.check_sum


class Heartbeat(JsonSerializable):
    @staticmethod
    def from_dict(dict_data):
        return Heartbeat()


class Hello(JsonSerializable):
    @staticmethod
    def from_dict(dict_data):
        return Hello()


class Goodbye(JsonSerializable):
    @staticmethod
    def from_dict(dict_data):
        return Goodbye()


class Health(JsonSerializable):
    @staticmethod
    def from_dict(dict_data):
        return Health()


class Task(JsonSerializable):
    def __init__(self, queue_uuid, create_time, trigger_time, task_uuid,
                 task_info, task_earliest, task_latest, session):
        # def __init__(self, queue_uuid, task_uuid, task_info, task_earliest, task_latest, session):
        self.queue_uuid = queue_uuid
        self.create_time = create_time
        self.trigger_time = trigger_time
        self.task_uuid = task_uuid
        self.task_info = task_info
        self.task_earliest = task_earliest
        self.task_latest = task_latest
        self.session = session

    @staticmethod
    def from_dict(dict_data):
        queue_uuid = dict_data['queue_uuid']
        create_time = dict_data['create_time']
        trigger_time = dict_data['trigger_time']
        task_uuid = dict_data['task_uuid']
        task_info = dict_data['task_info']
        task_earliest = dict_data['task_earliest']
        task_latest = dict_data['task_latest']
        session = dict_data['session']
        return Task(queue_uuid=queue_uuid, create_time=create_time, trigger_time=trigger_time, task_uuid=task_uuid,
                    task_info=task_info, task_earliest=task_earliest, task_latest=task_latest, session=session)


class TaskResult(JsonSerializable):
    def __init__(self, queue_uuid, task_uuid, status_code, status_msg, session, task_result=None):
        self.queue_uuid = queue_uuid
        self.task_uuid = task_uuid
        self.status_code = status_code
        self.status_msg = status_msg
        self.session = session
        self.task_result = task_result

    @staticmethod
    def from_dict(dict_data):
        queue_uuid = dict_data['queue_uuid']
        task_uuid = dict_data['task_uuid']
        status_code = TaskStatus(dict_data['status_code'])
        status_msg = dict_data['status_msg']
        session = dict_data['session']
        if dict_data['task_result']:
            task_result = Result()
            task_result.destination = dict_data['task_result']['destination']
            task_result.lines = dict_data['task_result']['lines']
            task_result.return_code = dict_data['task_result']['return_code']
            task_result.module = dict_data['task_result']['module']
            task_result.data = dict_data['task_result']['data']
            task_result.error_msg = dict_data['task_result']['error_msg']
        else:
            task_result = None
        return TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code, status_msg=status_msg,
                          session=session, task_result=task_result)
