# coding=utf-8

import os
import logging
from logging.handlers import TimedRotatingFileHandler

tm_logger = logging.getLogger('tm')
tm_logger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
tm_logger.addHandler(console)

Rthandler = TimedRotatingFileHandler(
    os.path.join(os.path.dirname(__file__), '../Logs/tmSyslog.log'),
    when='midnight',
    interval=1,
    backupCount=15,
    encoding='utf-8'
)
Rthandler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s'
)
Rthandler.setFormatter(formatter)
tm_logger.addHandler(Rthandler)
