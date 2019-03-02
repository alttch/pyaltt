__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.1.2"

import threading

from pyaltt.workers import background_worker

from pyaltt.workers import BackgroundWorker
from pyaltt.workers import BackgroundQueueWorker
from pyaltt.workers import BackgroundEventWorker

from pyaltt.functools import FunctionCollecton

g = threading.local()
