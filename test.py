import time
import logging

from pyaltt import background_worker
from pyaltt import background_task
from pyaltt import task_supervisor

import pyaltt

logging.basicConfig(level=logging.DEBUG)

# logging.getLogger('pyaltt/workers').setLevel(logging.DEBUG)
# logging.getLogger('pyaltt/supervisor').setLevel(logging.DEBUG)

import threading

from queue import Queue

myevent = threading.Event()

Q = Queue()

@background_worker(interval=2)
def worker(**kwargs):
    print('worker running')
    time.sleep(2.1)

@background_worker(queue=Q, priority=pyaltt.TASK_HIGH)
def myqueuedworker(task,**kwargs):
    print('queued worker running, task: {}'.format(task))

@background_worker(event=myevent)
def myeventworker(**kwargs):
    print('event worker running')
    time.sleep(1)

task_supervisor.set_config(pool_size=2, reserve_normal=0)
task_supervisor.poll_delay = 0.01
task_supervisor.start()

def test():
    print('test')

worker.start()
myqueuedworker.start()
myeventworker.start()
Q.put('task1')
myevent.set()
Q.put('task2')
Q.put('task3')
Q.put('task4')
print('ALL SET')
time.sleep(0.1)
background_task(test, name='ttt', wait_start=True)()
print('job ttt started')
time.sleep(5)
myqueuedworker.stop()
myeventworker.stop()
worker.stop()
