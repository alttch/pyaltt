__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.2.1"

import threading

from functools import wraps


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
        t.start()
        return t

    return start_thread
