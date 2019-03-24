__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.2.1"

import threading
import queue
import logging
import uuid
import time


class BackgroundWorker:

    def __init__(self, name=None, func=None, **kwargs):
        self.__thread = None
        self._active = False
        self.daemon = kwargs.get('daemon', True)
        self.o = kwargs.get('o')
        self.on_error = kwargs.get('on_error')
        self.on_error_kwargs = kwargs.get('on_error_kwargs', {})
        self.poll_delay = kwargs.get('poll_delay', 0.1)
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
        self.delay_before = kwargs.get('_delay_before', self.delay_before)
        self.delay = kwargs.get(
            '_interval',
            kwargs.get('_delay', kwargs.get('_delay_after', self.delay)))
        if '_interval' in kwargs:
            self.keep_interval = True
        if '_name' in kwargs:
            self.set_name(kwargs['_name'])
        self.realtime = kwargs.get('_realtime', self.realtime)
        if not (self._active and self.__thread and self.__thread.isAlive()):
            self.__thread = threading.Thread(
                target=self._start_worker,
                name=self.name,
                args=args,
                kwargs=kwargs)
            self.__thread.setDaemon(kwargs.get('_daemon', self.daemon))
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
        logging.debug(self.name + ' started')
        self.loop(*args, **kwargs)
        logging.debug(self.name + ' stopped')

    def loop(self, *args, **kwargs):
        kw = kwargs.copy()
        if not 'worker_name' in kw:
            kw['worker_name'] = self.name
        if not 'o' in kw:
            kw['o'] = self.o
        while self._active:
            try:
                if self.keep_interval: tstart = time.time()
                if self.delay_before:
                    if not self.sleep(self.delay_before): break
                if not self._active: break
                if self.run(*args, **kw) == False:
                    self._active = False
                    break
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
        kw = kwargs.copy()
        if not 'worker_name' in kw:
            kw['worker_name'] = self.name
        if not 'o' in kw:
            kw['o'] = self.o
        while self._active:
            try:
                task = self._Q.get()
                if not self._active: break
                if task is not None:
                    try:
                        if self.run(task, *args, **kw) == False:
                            self._active = False
                            break
                    except Exception as e:
                        self.error(e)
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
        kw = kwargs.copy()
        if not 'worker_name' in kw:
            kw['worker_name'] = self.name
        if not 'o' in kw:
            kw['o'] = self.o
        while self._active:
            try:
                self.event.wait()
                self.event.clear()
                if not self._active: break
                try:
                    if self.run(*args, **kw) == False:
                        self._active = False
                        break
                except Exception as e:
                    self.error(e)
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
