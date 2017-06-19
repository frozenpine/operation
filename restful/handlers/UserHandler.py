# -*- coding: UTF-8 -*-
#import logging

from flask import request
from flask_restful import Resource, reqparse
from werkzeug.exceptions import BadRequest
from werkzeug.security import check_password_hash

from app import db
from app.models import Operator
from restful.errors import (DataNotJsonError, DataNotNullError, DataTypeError,
                            DataUniqueError)


class UserApi(Resource):
    def get(self, **kwargs):
        user = Operator.find(**kwargs)
        if user:
            return {
                'message': 'user({}) found succeefully.'.format(user.name.encode('utf-8')),
                'data': user.to_json()
            }
        else:
            return {'message': 'user not found'}, 404

    def put(self, **kwargs):
        user = Operator.find(**kwargs)
        if user:
            try:
                data = request.get_json(force=True)
            except BadRequest:
                try:
                    raise DataNotJsonError
                except DataNotJsonError as e:
                    return {'error_code': e.error_code, 'message': e.message}
            else:
                try:
                    if 'old_password' in data:
                        if check_password_hash(user.password_hash, data.get('old_password')):
                            user.name = data.get('name', user.name)
                            user.disabled = data.get('disabled', user.disabled)
                            if 'password' in data:
                                user.password = data.get('password')
                            db.session.add(user)
                            db.session.commit()
                            return {'message': 'user ({}) updated successfully.'.format(user.login),
                                    'data': user.to_json()}
                        else:
                            return {'error_code': 1106, 'message': 'Old password must match.'}
                    else:
                        raise DataNotNullError
                except DataNotNullError as e:
                    return {'error_code': e.error_code, 'message': e.message}
                except TypeError:
                    try:
                        raise DataTypeError
                    except DataTypeError as e:
                        return {'error_code': e.error_code, 'message': e.message}
        else:
            return {'message': 'user not found'}, 404

class UserListApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'login', type=str, required=True,
            help='login name can not been none'
        )
        self.parser.add_argument(
            'name', type=str
        )
        self.parser.add_argument(
            'password', type=str, required=True,
            help='user pass can not been none'
        )
        super(UserListApi, self).__init__()

    def get(self):
        users = Operator.query.all()
        if users:
            return {
                'message': 'all users listed.',
                'data': {
                    'count': len(users),
                    'records': [user.to_json() for user in users]
                }
            }
        else:
            return {
                'message': 'no users.'
            }, 204

    def post(self):
        args = self.parser.parse_args()
        user = Operator(args['login'], args['password'], args['name'])
        db.session.add(user)
        db.session.commit()
