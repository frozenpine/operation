# -*- coding: UTF-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler
from enum import Enum

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='Logs/Syslog.log',
    filemode='a'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

Rthandler = TimedRotatingFileHandler(
    'Logs/Syslog.log',
    when='midnight',
    interval=1,
    backupCount=15,
    encoding='utf-8'
)
Rthandler.setLevel(logging.WARN)
formatter = logging.Formatter(
    '%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s'
)
Rthandler.setFormatter(formatter)
logging.getLogger('').addHandler(Rthandler)
