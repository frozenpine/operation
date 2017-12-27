# coding=utf-8

import sys
from os import path

try:
    from NewTaskManager.Controller.controller import Controller
except ImportError:
    sys.path.append(path.join(path.dirname(__file__), '../../../'))
    # from NewTaskManager.Controller.task_queue_manager import TaskQueueManager
    from NewTaskManager.Controller.controller import Controller

if __name__ == '__main__':
    # monkey.patch_all(socket=False, thread=False)
    # controller = TaskQueueManager()
    controller = Controller()
    controller.run()
