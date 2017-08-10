# -*- coding: UTF-8 -*-
from flask import request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from app import db
from app.models import SystemType
from restful.errors import (DataNotJsonError,
                            DataUniqueError,
                            DataNotNullError,
                            ApiError)
from restful.protocol import RestProtocol


class SystemTypeApi(Resource):
    def __init__(self):
        super(SystemTypeApi, self).__init__()

    def get(self, **kwargs):
        sys_type = SystemType.find(**kwargs)
        if sys_type:
            return RestProtocol(sys_type)
        else:
            return {'message': 'System type not found'}, 404

    def put(self, **kwargs):
        sys_type = SystemType.find(**kwargs)
        if sys_type:
            try:
                data = request.get_json(force=True)
                if data.get('name'):
                    if sys_type.name != data.get('name') and SystemType.find(name=data.get('name')):
                        raise DataUniqueError
            except BadRequest:
                return RestProtocol(DataNotJsonError())
            except DataUniqueError as e:
                return RestProtocol(e)
            else:
                sys_type.name = data.get('name', sys_type.name)
                sys_type.description = data.get('description', sys_type.description)
                db.session.add(sys_type)
                db.session.commit()
                return RestProtocol(sys_type)
        else:
            return {'message': 'System type not found'}, 404


class SystemTypeListApi(Resource):
    def __init__(self):
        super(SystemTypeListApi, self).__init__()
        self.not_null_list = ['name']

    def get(self):
        sys_types = SystemType.query.all()
        return RestProtocol(sys_types)

    def post(self):
        try:
            data = request.get_json(force=True)
            for param in self.not_null_list:
                if not data.get(param):
                    raise DataNotNullError('Please input {}'.format(param))
            if SystemType.find(name=data.get('name')):
                raise DataUniqueError
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        except ApiError as e:
            return RestProtocol(e)
        else:
            sys_type = SystemType()
            sys_type.name = data.get('name')
            sys_type.description = data.get('description')
            db.session.add(sys_type)
            db.session.commit()
            return RestProtocol(sys_type)
