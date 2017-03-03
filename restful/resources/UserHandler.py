from flask import request
from flask_restful import Resource, reqparse
import json

users = []

parser = reqparse.RequestParser()
parser.add_argument('username', type=str, required=True, dest='user_name', help='username can not been none', action='append')


class User(Resource):
    def get(self, user_id):
        try:
            return {'hello': users[user_id]}
        except IndexError:
            return {'error': 'user not found'}, 404
    def put(self, user_id):
        try:
            users[user_id] = request.form['username']
            return {'hello': users[user_id]}
        except IndexError:
            return {'error': 'user id not found'}, 404

class UserList(Resource):
    def get(self):
        return json.dumps(users)
    def post(self):
        args = parser.parse_args()
        users.extend(args['user_name'])