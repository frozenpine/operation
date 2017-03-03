from restful import app, restApi, handler

app.config.from_object('settings')

restApi.add_resource(handler.HelloUser, '/users/<int:user_id>')

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
