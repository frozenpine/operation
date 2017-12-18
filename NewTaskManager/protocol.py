# -*- coding: UTF-8 -*-

import json
import logging
import pickle
import time
from abc import ABCMeta, abstractmethod
from hashlib import md5
from os import path

import yaml
from enum import Enum

from excepts import DeserialError, InitialError

tm_logger = logging.getLogger('tm')


class MessageType(Enum):
    Broadcast = 0
    Private = 1


class PayloadType(Enum):
    Heartbeat = 0
    StaticsInfo = 1


class TmPayload(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_json(self):
        pass

    @abstractmethod
    def from_json(json_data):
        pass


class HeartBeatPL(TmPayload):
    def to_json(self):
        return {

        }


class TmProtocol(object):
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

    def __init__(self, src=None, dest=None, payload=None, msg_type=MessageType.Broadcast):
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

        if src:
            self.source = src
        else:
            raise InitialError('src')
        if dest:
            self.destination = dest
        else:
            raise InitialError('dest')
        self.message_type = msg_type
        if self.message_type == MessageType.Broadcast:
            self.destination = 'public'
        if payload:
            self.payload = payload
        else:
            raise InitialError('payload')
        hasher = md5(json.dumps(self.to_json(), sort_keys=True))
        self.check_sum = hasher.hexdigest()

    def to_json(self):
        """ Used to get protocol message's JSON data
        Args:
            dump_file: Save json data to an yaml file if dump_file is not None, and file path exists.

        Returns:
            Protocol message's JSON data w/o check_sum.
        """
        data = {
            'version': self.version,
            'source': self.source,
            'destination': self.destination,
            'message_type': self.message_type.name,
            'payload': self.payload.to_json() if isinstance(self.payload, TmPayload) else self.payload
        }
        return data

    @staticmethod
    def from_json(json_data):
        """ Create an class instance from dict
        Args:
            json_data: An dict object with specified key/value pairs
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
        src = json_data['source']
        dest = json_data['destination']
        msg_type = MessageType[json_data['message_type']]
        payload = TmPayload.from_json(json_data['payload'])

        return TmProtocol(src=src, dest=dest, payload=payload, msg_type=msg_type)

    def dump_file(self, dump_file=None):
        """ Dump protocol message to YAML file
        Args:
            dump_file: A dump file path, either directory path or file path is fine, defaults to None with save nothing
                if dump_file is a directory, YAML saved in name 'TmProtocol' and '_%Y%m%d%H%M%S' in time format.
                if dump_file is a file path and file exists, YAML saved with file name and
                '_%Y%m%d%H%M%S' in time format, old file will not be overwrited.
                if dump_file is a file path and file not exists, YAML saved in this particular dump file.

        Returns: None

        Raises:
            IOError: An error occour when dump file path invalid.
        """
        if dump_file:
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
                yaml.dump(self.to_json(), out_file, default_flow_style=False)

    def serial(self, is_json=False, dump_file=None):
        """ Used to serial protocol message
        Args:
            is_json (bool, optional):
                True 4 serial in json format w/o check_sum,
                False 4 serial in pickle formart w/ all attributes,
                defaults to False
            dump_file: An dump file path, either directory path or file path is fine, defaults to None with save nothing
                for more detail, see docstring in func dump_file

        Returns: Serialized protocol message.

        Raises:
            IOError: An error occour when dump file path invalid.
        """
        if is_json:
            self.dump_file(dump_file)
            return json.dumps(self.to_json())
        else:
            return pickle.dumps(self)

    @staticmethod
    def deserial(buff, is_json=False):
        """ Used to deserial protocol message from str buffer
        Args:
            is_json (bool, optional):
                True 4 deserial in json format w/o check_sum,
                False 4 deserial in pickle formart w/ all attributes,
                defaults to False

        Returns: Instance of class TmProtocol.

        Raises:
            DeserialError: An error occured deserilizing
        """
        if is_json:
            try:
                proto = TmProtocol.from_json(json.loads(buff))
            except KeyError as err:
                raise DeserialError('Invalid key name {}'.format(err.message))
            else:
                return proto
        else:
            data = pickle.loads(buff)
            if data.is_valid():
                return data
            else:
                raise DeserialError('Invalid data check sum in pickle dump.')

    def is_valid(self):
        """ Verifing protocol message is valid
        Args: None

        Returns: Ture 4 data is valid, False 4 data is invalid.
        """
        hasher = md5(json.dumps(self.to_json(), sort_keys=True))
        return hasher.hexdigest() == self.check_sum
