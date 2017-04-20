# -*- coding: UTF-8 -*-
import logging
from flask_restful import Resource, reqparse, request
from app import db
from app.models import User, Operator

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

    def put(self,**kwargs):
        pass

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
