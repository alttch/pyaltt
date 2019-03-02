__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.1.3"

import threading

from functools import wraps


class LocalProxy(threading.local):

    def get(self, attr, default=None):
        return getattr(self, attr, default)

    def has(self, attr):
        return hasattr(self, attr)

    def set(self, attr, value):
        return setattr(self, attr, value)


def background_job(f, *args, **kwargs):

    @wraps(f)
    def start_thread(_t_group=None, _t_name=None, _daemon=False, **kwargs):
        t = threading.Thread(
            group=_t_group, target=f, name=_t_name, kwargs=kwargs)
        if _daemon: t.setDaemon(True)
        t.start()
        return t

    return start_thread
