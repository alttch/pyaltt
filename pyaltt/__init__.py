__author__ = "Altertech Group, http://www.altertech.com/"
__copyright__ = "Copyright (C) 2018-2019 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.2.7"

from pyaltt.supervisor import WorkerSupervisor
from pyaltt.supervisor import TASK_LOW
from pyaltt.supervisor import TASK_NORMAL
from pyaltt.supervisor import TASK_HIGH
from pyaltt.supervisor import TASK_CRITICAL

task_supervisor = WorkerSupervisor()

from pyaltt.workers import background_worker

from pyaltt.workers import BackgroundWorker
from pyaltt.workers import BackgroundQueueWorker
from pyaltt.workers import BackgroundEventWorker

from pyaltt.f import FunctionCollecton

from pyaltt.threads import LocalProxy
from pyaltt.threads import background_task


g = LocalProxy()

