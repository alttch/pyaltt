__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.2.5"

import threading

from functools import wraps

from pyaltt import task_supervisor

from pyaltt import TASK_LOW
from pyaltt import TASK_NORMAL
from pyaltt import TASK_HIGH
from pyaltt import TASK_CRITICAL


class LocalProxy(threading.local):

    def get(self, attr, default=None):
        return getattr(self, attr, default)

    def has(self, attr):
        return hasattr(self, attr)

    def set(self, attr, value):
        return setattr(self, attr, value)

    def clear(self, attr):
        return delattr(self, attr) if hasattr(self, attr) else True


def background_job(f, *args, **kwargs):

    @wraps(f)
    def start_thread(*args, **kw):
        t = threading.Thread(
            group=kwargs.get('group'),
            target=f,
            name=kwargs.get('name'),
            args=args,
            kwargs=kw)
        if kwargs.get('daemon'): t.setDaemon(True)
        starter = threading.Thread(
            target=_background_job_starter,
            args=(t, kwargs.get('priority', TASK_LOW)))
        starter.setDaemon(True)
        starter.start()
        if kwargs.get('wait'):
            starter.join()
        return t

    return start_thread


def _background_job_starter(t, priority):
    if task_supervisor.acquire(t, priority):
        t.start()
        releaser = threading.Thread(target=_background_job_releaser, args=(t,))
        releaser.setDaemon(True)
        releaser.start()


def _background_job_releaser(t):
    t.join()
    task_supervisor.release(t)
