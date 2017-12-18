# coding=utf-8

import logging
import os
from logging.handlers import TimedRotatingFileHandler

controller_logger = logging.getLogger('controller')
controller_logger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)

controller_logger.addHandler(console)

controller_Rthandler = TimedRotatingFileHandler(
    os.path.join(os.path.dirname(__file__), '../Logs/controllerSyslog.log'),
    when='midnight',
    interval=1,
    backupCount=15,
    encoding='utf-8'
)

controller_Rthandler.setLevel(logging.INFO)
controller_Rthandler.setFormatter(formatter)
controller_logger.addHandler(controller_Rthandler)
