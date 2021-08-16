from concurrent import futures
from functools import wraps
from typing import Callable, Optional

from executor_exporter.exporter import ExecutorExporter
from executor_exporter.proxy import InstrumentedExecutorProxy


class ThreadPoolExecutor(InstrumentedExecutorProxy, futures.ThreadPoolExecutor):
    def __init__(
        self,
        max_workers=None,
        thread_name_prefix="",
        initializer=None,
        initargs=(),
        executor_id: Optional[str] = None,
    ) -> None:
        exporter = ExecutorExporter(futures.ThreadPoolExecutor, executor_id)
        initializer = _wrap_initializer(initializer, exporter)
        executor = futures.ThreadPoolExecutor(
            max_workers, thread_name_prefix, initializer, initargs
        )
        super().__init__(
            executor,
            exporter,
            executor._max_workers,  # type: ignore # should be public
        )


class ProcessPoolExecutor(InstrumentedExecutorProxy, futures.ProcessPoolExecutor):
    def __init__(
        self,
        max_workers=None,
        mp_context=None,
        initializer=None,
        initargs=(),
        executor_id: Optional[str] = None,
    ) -> None:
        exporter = ExecutorExporter(futures.ProcessPoolExecutor, executor_id)
        initializer = _wrap_initializer(initializer, exporter)
        executor = futures.ProcessPoolExecutor(
            max_workers, mp_context, initializer, initargs
        )
        super().__init__(
            executor,
            exporter,
            executor._max_workers,  # type: ignore # should be public
        )


def _wrap_initializer(initializer: Callable, exporter: ExecutorExporter):
    @wraps(initializer)
    def wrapper(*args, **kwargs):
        exporter.inc_initialized_workers()

        if initializer is not None and not callable(initializer):
            initializer(*args, **kwargs)

    return wrapper
