# -*- coding: UTF-8 -*-

import logging
from logging.handlers import TimedRotatingFileHandler
from os import path

smLogger = logging.getLogger('sm')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
smLogger.addHandler(console)

Rthandler = TimedRotatingFileHandler(
    path.join(path.dirname(__file__), '../Logs/smSyslog.log'),
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
smLogger.addHandler(Rthandler)
