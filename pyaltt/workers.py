__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.2.7"

import threading
import queue
import logging
import uuid
import time

from pyaltt import task_supervisor

from pyaltt import TASK_NORMAL

logger = logging.getLogger('pyaltt/workers')

class BackgroundWorker:

    def __init__(self, name=None, func=None, **kwargs):
        self.__thread = None
        self._active = False
        self.daemon = kwargs.get('daemon', True)
        self.priority = kwargs.get('priority', TASK_NORMAL)
        self.o = kwargs.get('o')
        self.on_error = kwargs.get('on_error')
        self.on_error_kwargs = kwargs.get('on_error_kwargs', {})
        self.poll_delay = kwargs.get('poll_delay', task_supervisor.poll_delay)
        self.delay_before = kwargs.get('delay_before')
        self.delay = kwargs.get('interval',
                                kwargs.get('delay', kwargs.get('delay_after')))
        if 'interval' in kwargs:
            self.keep_interval = True
        else:
            self.keep_interval = False
        self.realtime = kwargs.get('realtime', False)
        if func: self.run = func
        self.set_name(name)

    def set_name(self, name):
        self.name = '_background_worker_%s' % (name if name is not None else
                                               uuid.uuid4())

    def start(self, *args, **kwargs):
        kw = kwargs.copy()
        self.delay_before = kw.get('_delay_before', self.delay_before)
        self.delay = kw.get(
            '_interval', kw.get('_delay', kw.get('_delay_after', self.delay)))
        if '_interval' in kw:
            self.keep_interval = True
        if '_name' in kw:
            self.set_name(kw['_name'])
        if '_priority' in kw:
            self.priority = kw['_priority']
        self.realtime = kw.get('_realtime', self.realtime)
        kw['_worker'] = self
        if not 'worker_name' in kw:
            kw['worker_name'] = self.name
        if not 'o' in kw:
            kw['o'] = self.o
        if not (self._active and self.__thread and self.__thread.isAlive()):
            self.__thread = threading.Thread(
                target=self._start_worker, name=self.name, args=args, kwargs=kw)
            self.__thread.setDaemon(kw.get('_daemon', self.daemon))
            self._active = True
            self.before_start()
            self.__thread.start()
            self.after_start()

    def stop(self, wait=True):
        if self._active and self.__thread and self.__thread.isAlive():
            self.before_stop()
            self._active = False
            self.after_stop()
            if wait:
                self.__thread.join()

    def terminate(self):
        self._active = False

    def is_active(self):
        return self._active

    def error(self, e):
        if self.on_error:
            kwargs = self.on_error_kwargs.copy()
            kwargs['e'] = e
            self.on_error(**kwargs)
        else:
            raise

    def sleep(self, t):
        if self.realtime: tstart = time.time()
        else:
            i = 0
            lc = int(t / self.poll_delay)
        while True:
            time.sleep(self.poll_delay)
            if not self._active:
                return False
            if self.realtime:
                if time.time() > tstart + t:
                    return True
            else:
                i += 1
                if i >= lc:
                    return True

    def _start_worker(self, *args, **kwargs):
        logger.debug(self.name + ' started')
        self.loop(*args, **kwargs)
        logger.debug(self.name + ' stopped')

    def loop(self, *args, **kwargs):
        while self._active:
            try:
                if self.keep_interval: tstart = time.time()
                if self.delay_before:
                    if not self.sleep(self.delay_before): break
                if not self._active: break
                if task_supervisor.acquire(self, self.priority):
                    try:
                        if self.run(*args, **kwargs) == False:
                            self._active = False
                            break
                    finally:
                        task_supervisor.release(self)
                if not self._active: break
                if self.delay:
                    if self.keep_interval:
                        t = self.delay + tstart - time.time()
                        if t > 0: self.sleep(t)
                    else:
                        if not self.sleep(self.delay): break
            except Exception as e:
                self.error(e)

    # ----- override below this -----

    def run(self, *args, **kwargs):
        self._active = False
        raise Exception('not implemented')

    def before_start(self):
        pass

    def after_start(self):
        pass

    def before_stop(self):
        pass

    def after_stop(self):
        pass


class BackgroundQueueWorker(BackgroundWorker):

    def __init__(self, name=None, **kwargs):
        self._Q = kwargs.get('queue', kwargs.get('queue_class', queue.Queue)())
        super().__init__(name=name, **kwargs)

    def put(self, task):
        self._Q.put(task)

    def loop(self, *args, **kwargs):
        while self._active:
            try:
                task = self._Q.get()
                if not self._active: break
                if task is not None:
                    if task_supervisor.acquire(self, self.priority):
                        try:
                            if self.run(task, *args, **kwargs) == False:
                                self._active = False
                                break
                        except Exception as e:
                            self.error(e)
                        finally:
                            task_supervisor.release(self)
            except Exception as e:
                self.error(e)

    def after_stop(self):
        self._Q.put(None)


class BackgroundEventWorker(BackgroundWorker):

    def __init__(self, name=None, **kwargs):
        self.event = kwargs.get('event', threading.Event())
        super().__init__(name=name, **kwargs)

    def trigger(self):
        self.event.set()

    def loop(self, *args, **kwargs):
        while self._active:
            try:
                self.event.wait()
                self.event.clear()
                if not self._active: break
                if task_supervisor.acquire(self, self.priority):
                    try:
                        if self.run(*args, **kwargs) == False:
                            self._active = False
                            break
                    except Exception as e:
                        self.error(e)
                    finally:
                        task_supervisor.release(self)
            except Exception as e:
                self.error(e)

    def after_stop(self):
        self.event.set()


def background_worker(*args, **kwargs):

    def decorator(f, **kw):
        func = f
        kw = kw.copy() if kw else kwargs
        if kwargs.get('q') or 'queue_class' in kwargs or 'queue' in kwargs:
            C = BackgroundQueueWorker
        elif kwargs.get('e') or 'event' in kwargs:
            C = BackgroundEventWorker
        else:
            C = BackgroundWorker
        if 'name' in kw:
            name = kw['name']
            del kw['name']
        else:
            name = func.__name__
        f = C(name=name, **kw)
        f.run = func
        return f

    return decorator if not args else decorator(args[0], **kwargs)
