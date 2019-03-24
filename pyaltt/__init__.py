__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.2.1"

from pyaltt.workers import background_worker

from pyaltt.workers import BackgroundWorker
from pyaltt.workers import BackgroundQueueWorker
from pyaltt.workers import BackgroundEventWorker

from pyaltt.f import FunctionCollecton

from pyaltt.threads import LocalProxy
from pyaltt.threads import background_job

g = LocalProxy()
