from flask_restful import Resource, reqparse, request
from app.models import User

class UserApi(Resource):
    def get(self, login):
        user = User.find(login=login)
        if user:
            return {"login": user.login, "name": user.name}
        else:
            return {'error': 'user not found'}, 404
    def put(self, login):
        user = User.find(login=login)
        if user:
            user.name = request.form['username']
            user.save()
            return {"login": user.login, "name": user.name}
        else:
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
