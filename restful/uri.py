from .views import app
from flask_restful import Api
from resources.UserHandler import User, UserList

uri = Api(app)

uri.add_resource(User, '/api/users/<int:user_id>')
uri.add_resource(UserList, '/api/users')

