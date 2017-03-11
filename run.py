from app import app
from app.models import *

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
