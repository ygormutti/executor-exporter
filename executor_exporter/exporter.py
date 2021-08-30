from enum import Enum
from typing import Optional, Union

from prometheus_client import REGISTRY, Counter, Gauge, Histogram

PREFFIX = "python_executor_"


class Metrics:
    def __init__(self, registry=REGISTRY) -> None:
        self.max_workers_counter = Counter(
            PREFFIX + "max_workers_total",
            "Max workers accumulated by executor, i.e. instances with same executor_id",
            ("executor", "executor_type"),
            registry=registry,
        )

        self.initialized_workers_counter = Counter(
            PREFFIX + "initialized_workers_total",
            "Number of workers initialized by the executor",
            ("executor", "executor_type"),
            registry=registry,
        )

        self.submitted_tasks_counter = Counter(
            PREFFIX + "submitted_tasks_total",
            "Number of tasks submitted to the executor",
            ("executor", "executor_type"),
            registry=registry,
        )

        self.task_wait_histogram = Histogram(
            PREFFIX + "task_wait_seconds",
            "Time elapsed between tasks submission and start",
            ("executor", "executor_type"),
            registry=registry,
        )

        self.running_tasks_gauge = Gauge(
            PREFFIX + "running_tasks_total",
            "Number of started tasks not yet done",
            ("executor", "executor_type"),
            registry=registry,
        )

        self.tasks_duration_histogram = Histogram(
            PREFFIX + "tasks_duration_seconds",
            "Duration of tasks done by the executor, segmented by result (completed or failed)",
            ("executor", "executor_type", "result"),
            registry=registry,
        )

    def __iter__(self):
        yield from vars(self).values()


metrics = Metrics()


class TaskResult(Enum):
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutorExporter:
    def __init__(
        self,
        executor: Union[type, object],
        executor_id: Optional[str] = None,
        metrics: Metrics = metrics,
    ) -> None:
        self.labelvalues = (executor_id or "", type_fqn(executor))
        self.metrics = metrics

    def inc_max_workers(self, max_workers):
        self.metrics.max_workers_counter.labels(*self.labelvalues).inc(max_workers)

    def inc_initialized_workers(self):
        self.metrics.initialized_workers_counter.labels(*self.labelvalues).inc()

    def inc_submitted_tasks(self, by=1):
        self.metrics.submitted_tasks_counter.labels(*self.labelvalues).inc(by)

    def observe_task_wait(self, wait: float):
        self.metrics.task_wait_histogram.labels(*self.labelvalues).observe(wait)

    def inc_running_tasks(self):
        self.metrics.running_tasks_gauge.labels(*self.labelvalues).inc()

    def dec_running_tasks(self):
        self.metrics.running_tasks_gauge.labels(*self.labelvalues).dec()

    def observe_task_duration(self, result: TaskResult, duration: float):
        labelvalues = (*self.labelvalues, result.value)
        self.metrics.tasks_duration_histogram.labels(*labelvalues).observe(duration)


# ref: https://stackoverflow.com/a/2020083/358761
def type_fqn(obj: Union[type, object]) -> str:
    cls = obj if isinstance(obj, type) else obj.__class__
    module = cls.__module__
    if module == "builtins":
        return cls.__qualname__  # avoid outputs like 'builtins.str'
    return module + "." + cls.__qualname__
