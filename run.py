import os
from app import create_app

app = create_app('development')
host = os.environ.get('FLASK_HOST') or '0.0.0.0'
port = os.environ.get('FLASK_PORT') or 5000

if __name__ == '__main__':
    app.run(host=host, port=port)