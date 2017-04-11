import sys
sys.path.append('D:\\Users\\Sonny\\Documents\\Visual Studio 2015\\Projects\\Flask')
from enum import Enum
import logging
from logging.handlers import RotatingFileHandler
import re

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='Logs/Syslog.log',
    filemode='w'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

Rthandler = RotatingFileHandler('Logs/Syslog.log', maxBytes=300*1024*1024, backupCount=5)
Rthandler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s'
)
Rthandler.setFormatter(formatter)
logging.getLogger('').addHandler(Rthandler)

class ErrorCode(Enum):
    timeout = -2,
    invalid_login = -1,
    succeed = 0
    failed = 1

class Result():
    destination = None
    module = None
    params = {}
    return_code = 0
    error_code = ErrorCode
    error_msg = ""
    data = {}
    lines = []
