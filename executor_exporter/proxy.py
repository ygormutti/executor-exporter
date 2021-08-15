from concurrent import futures
from functools import wraps
from typing import Callable, Optional

from executor_exporter.exporter import ExecutorExporter, TaskStatuses


class InstrumentedExecutorProxy(futures.Executor):
    def __init__(
        self,
        executor: futures.Executor,
        exporter: ExecutorExporter,
        max_workers: Optional[int] = None,
    ) -> None:
        self.executor = executor
        self.exporter = exporter

        if max_workers is not None:
            self.exporter.set_max_workers_count(max_workers)

    def submit(self, fn, *args, **kwargs):
        self.exporter.inc_submitted_tasks_counter()
        fn = self._wrap_task(fn)
        return super().submit(fn, *args, **kwargs)

    def map(self, fn, *iterables, timeout=None, chunksize=1):
        items = list(iterables)
        self.exporter.inc_submitted_tasks_counter(by=len(items))
        fn = self._wrap_task(fn)
        return super().map(fn, items, timeout, chunksize)

    def _wrap_task(self, fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with self.exporter.task_duration_timer() as set_task_status:
                try:
                    self.exporter.inc_running_tasks()
                    retval = fn(*args, **kwargs)
                    set_task_status(1)
                    return retval
                except Exception:
                    set_task_status(TaskStatuses.FAILED)
                    raise
                finally:
                    self.exporter.dec_running_tasks()

        return wrapper
