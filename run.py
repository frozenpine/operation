import os
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from app import create_app

app = create_app('development')
host = os.environ.get('FLASK_HOST') or '0.0.0.0'
port = os.environ.get('FLASK_PORT') or 5000

if __name__ == '__main__':
    if app.config['DEBUG']:
        app.run(host=host, port=port)
    else:
        http_server = WSGIServer((host, port), app, handler_class=WebSocketHandler)
        http_server.serve_forever()
