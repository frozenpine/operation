from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, reqparse, request
from app.models import User
import json

auth = HTTPBasicAuth()

class UserApi(Resource):
    def get(self, login):
        try:
            user = User.find_user(login=login)
            return {"login": user.login, "name": user.name}
        except User.DoesNotExist:
            return {'error': 'user not found'}, 404
    def put(self, login):
        try:
            user = User.find_user(login=login)
            user.name = request.form['username']
            user.save()
            return {"login": user.login, "name": user.name}
        except User.DoesNotExist:
            return {'error': 'user not found'}, 404

class UserListApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True, dest='user_name', 
                                 help='username can not been none', action='append')
        super(UserListApi, self).__init__()

    def get(self):
        users = {"records": []}
        for user in User.nodes.filter():
            users['records'].append({"login": user.login, "name": user.name})
        return users
    def post(self):
        args = parser.parse_args()
        pass
