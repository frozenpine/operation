from app import app
from flask_restful import Api
from resources.UserHandler import UserById, UserList

uri = Api(app)

uri.add_resource(UserById, '/api/users/id/<int:user_id>')
uri.add_resource(UserList, '/api/users')

