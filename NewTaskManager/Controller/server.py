# coding=utf-8

import sys
from os import path

try:
    from NewTaskManager.Controller.controller import Controller
except ImportError:
    sys.path.append(path.join(path.dirname(__file__), '../../../'))
    from NewTaskManager.Controller.controller import Controller


if __name__ == '__main__':
    controller = Controller()
    controller.run()
