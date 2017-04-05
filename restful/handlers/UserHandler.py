from flask_restful import Resource, reqparse, request
from app import db
from app.models import User, Operator

class UserApi(Resource):
    def get(self, login):
        #user = User.find(login=login)
        user = Operator.find(login=login)
        if user:
            return {'login': user.login, 'name': user.name}
        else:
            return {'error': 'user not found'}, 404
    def put(self, login):
        #user = User.find(login=login)
        user = Operator.find(login=login)
        if user:
            user.name = request.form['username']
            #user.save()
            db.session.add(user)
            db.session.commit()
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
        #for user in User.nodes.filter():
        for user in Operator.query.all():
            users['records'].append({"login": user.login, "name": user.name})
        return users
    def post(self):
        args = parser.parse_args()
        pass
