import os
from neomodel import config as neoconfig
base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'SOMEthing-you-WILL-never-Guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('FLASK_SQLALCHEMY_DATABASE_URI') or \
         'sqlite:///' + os.path.join(base_dir, 'database/flask.db')
    NEO4J_DATABASE_URI = 'bolt://{0}:{1}@192.168.101.152:7687'
    NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME') or 'neo4j'
    NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD') or '022010144blue'

    @classmethod
    def init_app(cls, app):
        neoconfig.DATABASE_URL = \
            cls.NEO4J_DATABASE_URI.format(cls.NEO4J_USERNAME, cls.NEO4J_PASSWORD)
        neoconfig.FORCE_TIMEZONE = True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
