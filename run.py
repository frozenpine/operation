from os import environ
import sys
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from gevent import version_info
from gevent import monkey
from app import create_app

host = environ.get('FLASK_HOST') or '0.0.0.0'
port = environ.get('FLASK_PORT') or 5000

if __name__ == '__main__':
    app = create_app(sys.argv[1])
    if app.config['DEBUG']:
        app.run(host=host, port=port, threaded=True)
    else:
        monkey.patch_all()
        http_server = WSGIServer((host, port), app, handler_class=WebSocketHandler,)
        http_server.serve_forever()
