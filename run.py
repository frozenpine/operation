from restful import app

app.config.from_object('settings')

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
