import os
from neomodel import config as neoconfig
base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'SOMEthing-you-WILL-never-Guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('FLASK_SQLALCHEMY_DATABASE_URI') or \
         'sqlite:///' + os.path.join(base_dir, 'database/flask.db')
    NEO4J_DATABASE_URI = 'bolt://{0}:{1}@{2}:{3}'
    NEO4J_HOST = os.environ.get('NEO4J_HOST')
    NEO4J_PORT = os.environ.get('NEO4J_PORT') or '7687'
    NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME') or 'neo4j'
    NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD') or '022010144blue'
    JINJA_VAR_START = os.environ.get('JINJA_VAR_START') or '[['
    JINJA_VAR_STOP = os.environ.get('JINJA_VAR_STOP') or ']]'

    @classmethod
    def init_app(cls, app):
        neoconfig.DATABASE_URL = \
            cls.NEO4J_DATABASE_URI.format(cls.NEO4J_USERNAME, cls.NEO4J_PASSWORD,
                                          cls.NEO4J_HOST, cls.NEO4J_PORT)
        neoconfig.FORCE_TIMEZONE = True
        app.jinja_env.variable_start_string = cls.JINJA_VAR_START
        app.jinja_env.variable_end_string = cls.JINJA_VAR_STOP

class DevelopmentConfig(Config):
    DEBUG = True
    NEO4J_HOST = '192.168.101.152'

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
