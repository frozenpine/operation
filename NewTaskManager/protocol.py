# coding=utf-8
"""
Protocol definetion used between TaskManager's Master Node and Work Node.
"""

import json
import pickle
import time
from abc import ABCMeta, abstractmethod
from hashlib import md5
from os import path

import yaml
from enum import Enum

from NewTaskManager import tm_logger
from NewTaskManager.excepts import DeserialError, InitialError


class MessageType(Enum):
    Broadcast = 0
    Private = 1


class PayloadType(Enum):
    Heartbeat = 0
    StaticsInfo = 1


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
                elif isinstance(obj, Enum):
                    results[field] = obj.value
                else:
                    results[field] = obj
        return results

    @staticmethod
    @abstractmethod
    def from_dict(dict_data):
        """ An abstract method define, used to convert particular json to class instance
        """
        pass

    def serial(self):
        """ Used to serial object instance
        Args: None

        Returns: Serialized object instance
        """
        return pickle.dumps(self)

    @classmethod
    def deserial(cls, buff):
        """ Used to deserial protocol message from str buffer
        Args:
            buff: pickle serialized buff string.

        Returns: Instance of class.

        Raises:
            DeserialError: An error occured when deserialized instance is not type of cls
        """
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
            file_name = 'TmProtocol_{timestamp}.yaml'.format(timestamp=time.strftime('%Y%m%d%H%M%S'))
        else:
            directory = path.dirname(dump_file)
            if path.isdir(directory):
                if path.isfile(dump_file):
                    file_name = '{file_name}_{timestamp}.yaml'.format(
                        file_name=path.basename(dump_file).split('.')[0],
                        timestamp=time.strftime('%Y%m%d%H%M%S'))
                else:
                    file_name = path.basename(dump_file)
            else:
                message = '"{}" is neither an dir nor a regular file.'.format(dump_file)
                tm_logger.error(message)
                raise IOError(message)
        with open('{dir}/{file}'.format(dir=directory, file=file_name), mode='wb') as out_file:
            message = 'Data is dumped into yaml file({dir}/{file})'.format(dir=directory, file=file_name)
            tm_logger.info(message)
            yaml.dump(self.to_dict(), out_file, default_flow_style=False)


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
        hasher = md5(json.dumps(self, cls=JsonSerializableEncoder, sort_keys=True))
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
        hasher = md5(json.dumps(self, cls=JsonSerializableEncoder, sort_keys=True))
        return hasher.hexdigest() == self.check_sum


class Heartbeat(JsonSerializable):
    @staticmethod
    def from_dict(dict_data):
        return Heartbeat()
