from flask import request
from flask_restful import Resource, reqparse
import json

users = {}

parser = reqparse.RequestParser()
parser.add_argument('username', type=str, required=True, dest='user_name', help='username can not been none', action='append')


class UserById(Resource):
    def get(self, user_id):
        if users.has_key(user_id):
            return {'hello': users[user_id]}
        else:
            return {'error': 'user not found'}, 404
    def put(self, user_id):
        if users.has_key(user_id):
            users[user_id] = request.form['username']
            return {'hello': users[user_id]}
        else:
            return {'error': 'user id not found'}, 404

class UserList(Resource):
    def get(self):
        return users
    def post(self):
        args = parser.parse_args()
        pass