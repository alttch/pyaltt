# pyaltt
Various tools for functions, looped and queued workers etc.

License: Apache License 2.0

FunctionCollection
==================

Collect and run a pack of functions

Usage example:
 
```python
from pyaltt import FunctionCollecton

funcs = FunctionCollecton()

@funcs
def f1():
    print('I am function 1')

@funcs
def f2():
    print('I am function 2')

funcs.run()
```

Real life example: define **shutdown** function collection and call
*shutdown.run()* to stop all background threads.

Parameters:

* **on_error** function which is called if any function throws an exeption
  (with e=Exception argument), or if **remove** method is called and function
  doesn't exist in collection.
* **on_error_kwargs** additional arguments for *on_error*

Background workers
==================

Looped worker decorator
-----------------------

Simple background worker which executes method in loop, with an interval/delay
if set.

Usage example:

```python
from pyaltt import background_worker

#transforms function into background worker which run in a loop
@background_worker
def myworker(**kwargs):
    print('I\'m a worker ' + kwargs.get('worker_name'))

myworker.start()
# ................
myworker.stop()
```

Parameters for @background_worker:

* **name** alternative worker name (default is function name)
* **daemon** set background worker as daemon (default is *True*)
* **o** any object which worker can get with *kwargs.get('o')*
* **on_error** function which is called if worker throws an exeption (with
  e=Exception argument)
* **on_error_kwargs** additional arguments for *on_error*
* **delay_before** delay before each worker function execution
* **delay_after** (or simply **delay**) delay after each worker function
  execution
* **interval** same as **delay_after** but it will try to keep execution
  interval exactly
* **poll_delay** sleep precision (lower is better but uses CPU, default is 0.1
  sec)
* **realtime** Use different algorythm for sleeping to be even more exact

Note: if running in virtual machine, unset "sync guest time with host"
otherwise real time sleep may work unpredictable.

Poll delay should be lower or equal to delays. If you set very short delays,
don't forget to decrease poll delay as well.

Real time loop execution in this library is not 100% exact and can't be used
e.g. in heavy industry. Real time loops require dedicated coding for the
particular task and for small delays can't be coded with Python at all or
require special tricks/hardware.

Parameters for start():

* **_daemon** override initial params and set worker as daemon or not
* delay, interval and realtime parameters can be overriden in start (use kwargs
  with *_*: _delay, _interval etc.)

* All other parameters are passed to worker function (both args and kwargs)

Worker gets all parameters used in *start()* plus additionally, **worker_name**
and **o** in kwargs (can be overriden in *start()*).

Paramter *wait=False* can be used for *stop()* to send a signal to worker and
continue (default is wait until worker finish)

Queue worker decorator
----------------------

Background worker which processes tasks in a queue.

Usage example:

```python
from pyaltt import background_worker

#transforms function into background worker which run on task in queue
@background_worker(q=True)
def myworker(task, **kwargs):
    print('Got a task %s' % task)

myworker.start()
# ................
myworker.put('task 1')
# ................
myworker.stop()
```

Parameters:

* **name**, **daemon**, **o**, **on_error**, **on_error_kwargs** same as for
  looped worker
* **queue_class** use alternative queue class (e.g. queue.PriorityQueue,
  default is *queue,Queue*).
* **queue** use external queue

If *queue* or *queue_class* parameters are set, *q=True* is not required.

Task can be any object (obvious). Worker has task always as first parameter.

Parameters for start() / stop() are the same as for looped worker.

Event worker decorator
----------------------

Background worker which runs method on event.

```python
from pyaltt import background_worker

#transforms function into background worker which run on task in queue
@background_worker(e=True)
def myworker(**kwargs):
    print('event triggered')

myworker.start()
# ................
myworker.trigger()
# ................
myworker.stop()
```

Parameters:

* **name**, **daemon**, **o**, **on_error**, **on_error_kwargs** same as for
  looped worker
* **event** use external *threading.Event()* object. If this parameter is set,
  *e=True* is not required.

Parameters for start() / stop() are the same as for looped worker.


Stopping loop from worker
-------------------------

This can be done in 2 ways: calling *myworker.terminate()* from worker function
or simply return *False*.

Working directly with classes
-----------------------------

Background worker classes can be used without a wrapper.

You can override **loop** method to have own function executed when worker
starts.

Loop calls **run** function which's actually a worker function (the same
decorated/transformed in the examples above).

(c) 2018-2019 Altertech Group, https://www.altertech.com/

