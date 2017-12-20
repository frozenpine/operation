# coding=utf-8

import logging
from logging.handlers import TimedRotatingFileHandler

import os

worker_logger = logging.getLogger('worker')
worker_logger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s [%(process)d %(thread)d] [%(filename)s %(funcName)s %(lineno)d] [%(message)s]', '%c'
)
console.setFormatter(formatter)

worker_logger.addHandler(console)

worker_Rthandler = TimedRotatingFileHandler(
    os.path.join(os.path.dirname(__file__), '../Logs/workerSyslog.log'),
    when='midnight',
    interval=1,
    backupCount=15,
    encoding='utf-8'
)

worker_Rthandler.setLevel(logging.INFO)
worker_Rthandler.setFormatter(formatter)
worker_logger.addHandler(worker_Rthandler)
