__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.0.2"

import threading
import queue
import logging
import uuid
import time


class BackgroundWorker:

    def __init__(self, name=None, func=None, **kwargs):
        self.__thread = None
        self.__active = False
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
        self.name = '_background_worker_%s' % (name if name is not None else
                                               uuid.uuid4())

    def start(self, *args, **kwargs):
        self.delay_before = kwargs.get('_delay_before', self.delay_before)
        self.delay = kwargs.get(
            '_interval',
            kwargs.get('_delay', kwargs.get('_delay_after', self.delay)))
        if '_interval' in kwargs:
            self.keep_interval = True
        self.realtime = kwargs.get('_realtime', self.realtime)
        if not (self.__active and self.__thread and self.__thread.isAlive()):
            self.__thread = threading.Thread(
                target=self._start_worker,
                name=self.name,
                args=args,
                kwargs=kwargs)
            self.__thread.setDaemon(kwargs.get('_daemon', self.daemon))
            self.__active = True
            self.before_start()
            self.__thread.start()
            self.after_start()

    def stop(self, wait=True):
        if self.__active and self.__thread and self.__thread.isAlive():
            self.before_stop()
            self.__active = False
            self.after_stop()
            if wait:
                self.__thread.join()

    def is_active(self):
        return self.__active

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
            if not self.is_active():
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
        while self.is_active():
            try:
                if self.keep_interval: tstart = time.time()
                if self.delay_before:
                    if not self.sleep(self.delay_before): break
                self.run(*args, **kw)
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
        self.__active = False
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
        self._Q = kwargs.get('queue_class', queue.Queue)()
        super().__init__(name=name, **kwargs)

    def put(self, task):
        self._Q.put(task)

    def loop(self, *args, **kwargs):
        kw = kwargs.copy()
        if not 'worker_name' in kw:
            kw['worker_name'] = self.name
        if not 'o' in kw:
            kw['o'] = self.o
        while self.is_active():
            try:
                task = self._Q.get()
                if not self.is_active(): break
                if task is not None:
                    try:
                        self.run(task, *args, **kw)
                    except Exception as e:
                        self.error(e)
            except Exception as e:
                self.error(e)

    def after_stop(self):
        self._Q.put(None)


def background_worker(*args, **kwargs):

    def decorator(f):
        func = f
        kw = kwargs.copy()
        if kwargs.get('q') or 'queue_class' in kwargs:
            C = BackgroundQueueWorker
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
