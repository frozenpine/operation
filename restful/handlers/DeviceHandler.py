# -*- coding: UTF-8 -*-
import re

from flask import request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from app import db
from app.models import Server, PlatformType
from restful.errors import (DataNotJsonError,
                            DataUniqueError,
                            DataNotNullError,
                            DataEnumValueError,
                            DataTypeError,
                            ApiError)
from restful.protocol import RestProtocol


class DeviceApi(Resource):
    def __init__(self):
        super(DeviceApi, self).__init__()
        self.pattern = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')

    def get(self, **kwargs):
        dev = Server.find(**kwargs)
        if dev:
            return RestProtocol(dev)
        else:
            return RestProtocol(message='Server not found', error_code=-1), 404

    def put(self, **kwargs):
        device = Server.find(**kwargs)
        if device:
            try:
                data = request.get_json(force=True)
                if data.get('name'):
                    if device.name != data.get('name') and Server.find(name=data.get('name')):
                        raise DataUniqueError
                if data.get('ip'):
                    if not self.pattern.match(data.get('ip')):
                        raise DataTypeError('Please enter a valid IP address.')
                if data.get('platform'):
                    PlatformType[data.get('platform')]
            except BadRequest:
                return RestProtocol(DataNotJsonError())
            except ApiError as e:
                return RestProtocol(e)
            except KeyError:
                return RestProtocol(DataEnumValueError())
            else:
                device.name = data.get('name', device.name)
                device.user = data.get('user', device.user)
                device.password = data.get('password') if data.get('password') else device.password
                device.ip = data.get('ip', device.ip)
                device.description = data.get('description', device.description)
                device.disabled = data.get('disabled', device.disabled)
                db.session.add(device)
                db.session.commit()
                return RestProtocol(device)
        else:
            return {'message': 'Server not found'}, 404


class DeviceListApi(Resource):
    def __init__(self):
        super(DeviceListApi, self).__init__()
        self.not_null_list = ['name', 'user', 'password', 'ip', 'platform']
        self.pattern = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')

    def get(self):
        devices = Server.query.filter(Server.disabled == False).all()
        return RestProtocol(devices)

    def post(self):
        try:
            data = request.get_json(force=True)
            for param in self.not_null_list:
                if not data.get(param):
                    raise DataNotNullError('Please input {}'.format(param))
            if Server.find(name=data.get('name')):
                raise DataUniqueError
            if not self.pattern.match(data.get('ip')):
                raise DataTypeError('Please enter a valid IP address.')
            PlatformType[data.get('platform')]
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        except ApiError as e:
            return RestProtocol(e)
        except KeyError:
            return RestProtocol(DataEnumValueError())
        else:
            device = Server()
            device.name = data.get('name')
            device.user = data.get('user')
            device.password = data.get('password')
            device.ip = data.get('ip')
            device.description = data.get('description')
            device.platform = PlatformType[data.get('platform')]
            db.session.add(device)
            db.session.commit()
            return RestProtocol(device)
