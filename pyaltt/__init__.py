__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.1.1"

import threading

from pyaltt.workers import background_worker

from pyaltt.workers import BackgroundWorker
from pyaltt.workers import BackgroundQueueWorker
from pyaltt.workers import BackgroundEventWorker

from pyaltt.functools import FunctionCollecton

g = threading.local()


def g_getattr(attr, default=None):
    return getattr(g, attr, default)


def g_setattr(attr, value):
    return setattr(g, attr, value)


def g_hasattr(attr):
    return hasattr(g, attr)


g.get = g_getattr
g.set = g_setattr
g.has = g_hasattr
