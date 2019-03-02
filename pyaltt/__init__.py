__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.0.7"

import threading

from pyaltt.workers import background_worker
from pyaltt.functools import FunctionCollecton

g = threading.local()
