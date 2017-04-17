# -*- coding: UTF-8 -*-
from flask_restful import Resource, reqparse, request
from app import db
from app.models import User, Operator

class UserApi(Resource):
    def get(self, **kwargs):
        #user = User.find(login=login)
        user = Operator.find(**kwargs)
        if user:
            return {
                'message': 'user({}) found succeefully.'.format(user.name.encode('utf-8')),
                'data': user.to_json()
            }
        else:
            return {'message': 'user not found'}, 404
    '''
    def put(self, **kwargs):
        #user = User.find(login=login)
        user = Operator.find(**kwargs)
        if user:
            user.name = request.form['username']
            #user.save()
            db.session.add(user)
            db.session.commit()
            return {'message': 'user({}) updated successfully.'.format(user.name), 'data': user.to_json()}
        else:
            return {'message': 'user not found'}, 404
    '''

class UserListApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True, dest='user_name',
                                 help='username can not been none', action='append')
        super(UserListApi, self).__init__()

    def get(self):
        users = Operator.query.all()
        #for user in User.nodes.filter():
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
        args = parser.parse_args()
        pass
