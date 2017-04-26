from os import environ
import sys
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from gevent import version_info
from gevent import monkey
monkey.patch_all()
from app import create_app

host = environ.get('FLASK_HOST') or '0.0.0.0'
port = environ.get('FLASK_PORT') or 5000

if __name__ == '__main__':
    app = create_app(sys.argv[1])
    if app.config['DEBUG']:
        app.run(host=host, port=port, threaded=True)
    else:
        '''
        base_env = {
            'GATEWAY_INTERFACE': 'CGI/1.1',
            'SERVER_SOFTWARE': 'gevent/%d.%d Python/%d.%d' % \
                (version_info[:2] + sys.version_info[:2]),
            'SCRIPT_NAME': '',
            'wsgi.version': (1, 0),
            'wsgi.multithread': True,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False
        }
        '''
        http_server = WSGIServer((host, port), app, handler_class=WebSocketHandler,)
        http_server.serve_forever()
