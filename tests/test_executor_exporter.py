from concurrent.futures import Executor

from prometheus_client import CollectorRegistry, generate_latest

from executor_exporter import __version__, ExecutorExporter
from executor_exporter.exporter import Metrics


def test_version():
    assert __version__ == "0.1.0"


def test_executor_exporter(snapshot):
    registry = CollectorRegistry()
    metrics = Metrics(registry)
    exporter = ExecutorExporter(DummyExecutor(), "test-executor-id", metrics)
    
    exporter.inc_max_workers

    snapshot.assert_match(generate_latest(registry))


class DummyExecutor(Executor):
    pass
