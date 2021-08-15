from enum import Enum
from timeit import default_timer
from typing import Callable, Generator, Optional, Union

from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
)

PREFFIX = "python_executor_"


class TaskStatuses(Enum):
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutorExporter:
    def __init__(
        self,
        executor: Union[type, object],
        executor_id: Optional[str] = None,
        registry: Optional[CollectorRegistry] = None,
    ) -> None:
        self.labelvalues = (executor_id or "", type_fqn(executor))

        if registry is None:
            registry = REGISTRY

        self.max_workers_counter = Info(
            PREFFIX + "max_workers",
            "Total of workers the executor can have simultaneously",
            ("executor", "executor_type"),
            registry=registry,
        )

        self.initialized_workers_counter = Counter(
            PREFFIX + "initialized_workers_count",
            "Total of workers initialized by the executor",
            ("executor", "executor_type"),
            registry=registry,
        )

        self.submitted_tasks_counter = Counter(
            PREFFIX + "submitted_tasks_count",
            "Total of tasks submitted to the executor",
            ("executor", "executor_type"),
            registry=registry,
        )

        self.running_tasks_gauge = Gauge(
            PREFFIX + "running_tasks_count",
            "Total of started tasks not yet done",
            ("executor", "executor_type"),
            registry=registry,
        )

        self.tasks_duration_histogram = Histogram(
            PREFFIX + "tasks_duration_seconds",
            "Duration of tasks done by the executor, segmented by status",
            ("executor", "executor_type"),
            registry=registry,
        )

        self.supported_metrics = (
            self.max_workers_counter,
            self.initialized_workers_counter,
            self.submitted_tasks_counter,
            self.running_tasks_gauge,
            self.tasks_duration_histogram,
        )

    def set_max_workers_count(self, max_workers):
        self.max_workers_counter.labels(*self.labelvalues).info(max_workers)

    def inc_initialized_workers_counter(self):
        self.initialized_workers_counter.labels(*self.labelvalues).inc()

    def inc_submitted_tasks_counter(self, by=1):
        self.submitted_tasks_counter.labels(*self.labelvalues).inc(by)

    def inc_running_tasks(self):
        self.running_tasks_gauge.labels(*self.labelvalues).inc()

    def dec_running_tasks(self):
        self.running_tasks_gauge.labels(*self.labelvalues).dec()

    def task_duration_timer(
        self,
    ) -> Generator[Callable[[TaskStatuses], None], None, None]:
        status = TaskStatuses.FAILED

        def set_status(new_status: TaskStatuses):
            nonlocal status
            status = new_status

        start = default_timer()
        try:
            yield set_status
        finally:
            duration = default_timer() - start
            labelvalues = (*self.labelvalues, status.value)
            self.tasks_duration_histogram.labels(labelvalues).observe(duration)


# ref: https://stackoverflow.com/a/2020083/358761
def type_fqn(obj: Union[type, object]) -> str:
    cls = obj if isinstance(obj, type) else obj.__class__
    module = cls.__module__
    if module == "builtins":
        return cls.__qualname__  # avoid outputs like 'builtins.str'
    return module + "." + cls.__qualname__
