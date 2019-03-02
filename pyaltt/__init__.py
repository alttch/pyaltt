__version__ = "0.0.5"

import threading

from pyaltt.workers import background_worker
from pyaltt.functools import FunctionCollecton

g = threading.local()
