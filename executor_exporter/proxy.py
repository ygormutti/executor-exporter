from concurrent import futures
from functools import wraps
from sys import version_info
from timeit import default_timer as time
from typing import Callable, Optional

from executor_exporter.exporter import ExecutorExporter, TaskResult

PY_3_9 = version_info.minor >= 9


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
            self.exporter.inc_max_workers(max_workers)

    def submit(self, fn, /, *args, **kwargs):
        self.exporter.inc_submitted_tasks()
        fn = self._wrap_task(fn, time())
        return self.executor.submit(fn, *args, **kwargs)

    def map(self, fn, *iterables, timeout=None, chunksize=1):
        items = list(iterables)
        self.exporter.inc_submitted_tasks(by=len(items))
        fn = self._wrap_task(fn, time())
        return self.executor.map(fn, items, timeout, chunksize)

    def _wrap_task(self, fn: Callable, submitted: float) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            wait = time() - submitted
            self.exporter.observe_task_wait(wait)
            self.exporter.inc_running_tasks()
            start = time()
            try:
                retval = fn(*args, **kwargs)
                result = TaskResult.COMPLETED
                return retval
            except Exception:
                result = TaskResult.FAILED
                raise
            finally:
                duration = time() - start
                self.exporter.observe_task_duration(result, duration)
                self.exporter.dec_running_tasks()

        return wrapper

    if PY_3_9:  # Python 3.9 added `, *, cancel_futures=False` to signature

        def shutdown(self, wait=True, *, cancel_futures=False) -> None:
            return self.executor.shutdown(
                wait, cancel_futures=cancel_futures
            )  # type: ignore # mypy validates signature against installed version

    else:

        def shutdown(  # type: ignore # these variants cannot have the same signature
            self, wait=True
        ) -> None:
            return self.executor.shutdown(wait)
