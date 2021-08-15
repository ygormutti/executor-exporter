import importlib.metadata

from executor_exporter.executors import ProcessPoolExecutor, ThreadPoolExecutor
from executor_exporter.exporter import ExecutorExporter
from executor_exporter.proxy import InstrumentedExecutorProxy

# ref: https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
__version__ = importlib.metadata.version(__name__)

__all__ = (
    "ExecutorExporter",
    "InstrumentedExecutorProxy",
    "ProcessPoolExecutor",
    "ThreadPoolExecutor",
)
