from flask import request
from flask_restful import Resource

users = {}

class HelloUser(Resource):
    def get(self, user_id):
        if(users.has_key(user_id)):
            return {'hello': users[user_id]}
        else:
            return {'error': 'user not found'}, 404
    def put(self, user_id):
        users[user_id] = request.form['username']
        return {'hello': users[user_id]}