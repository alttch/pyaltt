__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.2.7"

import threading
import time
import logging

TASK_LOW = 0
TASK_NORMAL = 10
TASK_HIGH = 30
TASK_CRITICAL = 50

logger = logging.getLogger('pyaltt/supervisor')


class WorkerSupervisor:

    def __init__(self,
                 pool_size=2,
                 reserve_normal=5,
                 reserve_high=10,
                 poll_delay=0.1):

        self.active_tasks = set()
        self.active = False
        self.lock = threading.Lock()
        self.poll_delay = poll_delay
        self.max_tasks = {}
        self.queue = {TASK_LOW: [], TASK_NORMAL: [], TASK_HIGH: []}
        self.set_config(
            pool_size=pool_size,
            reserve_normal=reserve_normal,
            reserve_high=reserve_high)

    def higher_queues_busy(self, task_priority):
        if task_priority == TASK_NORMAL:
            return len(self.queue[TASK_HIGH]) > 0
        elif task_priority == TASK_LOW:
            return len(self.queue[TASK_NORMAL]) > 0 or \
                    len(self.queue[TASK_HIGH]) > 0
        else:
            return False

    def acquire(self, task, task_priority):
        if self.active and task_priority != TASK_CRITICAL:
            self.lock.acquire()
            self.queue[task_priority].append(task)
            while self.active and \
                    (len(self.active_tasks) >= self.max_tasks[task_priority] \
                        or self.queue[task_priority][0] != task or \
                        self.higher_queues_busy(task_priority)):
                self.lock.release()
                time.sleep(self.poll_delay)
                self.lock.acquire()
            try:
                self.queue[task_priority].pop(0)
                if not self.active:
                    return False
                self.active_tasks.add(task)
                logger.debug('new task {} pool size: {} / {}'.format(
                    task, len(self.active_tasks), self.pool_size))
            finally:
                self.lock.release()
        return True

    def release(self, task):
        if self.active:
            with self.lock:
                if task in self.active_tasks:
                    self.active_tasks.remove(task)
                    logger.debug('removed task {} pool size: {} / {}'.format(
                        task, len(self.active_tasks), self.pool_size))
        return True

    def set_config(self, **kwargs):
        for p in ['pool_size', 'reserve_normal', 'reserve_high']:
            if p in kwargs:
                setattr(self, p, int(kwargs[p]))
        self.max_tasks[TASK_LOW] = self.pool_size
        self.max_tasks[TASK_NORMAL] = self.pool_size + self.reserve_normal
        self.max_tasks[TASK_HIGH] = self.pool_size + \
                self.reserve_normal + self.reserve_high

    def start(self):
        self.active = True

    def stop(self, wait=True):
        self.active = False
        if wait:
            while True:
                with self.lock:
                    if not self.active_tasks:
                        break
                time.sleep(self.poll_delay)
