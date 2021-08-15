# executor-exporter
[![codecov](https://codecov.io/gh/ygormutti/executor-exporter/branch/main/graph/badge.svg?token=FIXME)](https://codecov.io/gh/ygormutti/executor-exporter)
[![CI](https://github.com/ygormutti/executor-exporter/actions/workflows/main.yml/badge.svg)](https://github.com/ygormutti/executor-exporter/actions/workflows/main.yml)

A [Prometheus](https://prometheus.io/) exporter for Python [`concurrent.futures`](https://docs.python.org/3/library/concurrent.futures.html) executors. Provides instrumented drop-in replacements for `ThreadedPoolExecutor` and `ProcessPoolExecutor`.

![water level ruler photo](docs/water_level_ruler.jpg)

*Public domain photo by Patsy Lynch. [More info](https://commons.wikimedia.org/wiki/File:FEMA_-_40847_-_A_water_level_ruler_in_North_Dakota.jpg)*

## Install it from PyPI

```bash
pip install executor-exporter
```

## Usage

```py
from executor_exporter import ThreadPoolExecutor
# or
from executor_exporter import ProcessPoolExecutor
```

If you stick to the public APIs of `concurrent.future` executors (consisting of `__init__`, `submit` and `map` methods), you just need to replace the builtin executor with its instrumented version provided by this package.

The provided executors act as [proxies](https://en.wikipedia.org/wiki/Proxy_pattern) for the builtin executor while collecting the following metrics:

<!-- begin metrics_table -->
<!-- end metrics_table -->

### Additional parameters

The `__init__` methods of the instrumented executors take two additional optional parameters:

| Parameter     | Type                                  | Default value                                   | Description                                                                                                                                                                                                   |
| ------------- | ------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `exporter_id` | `str`                                 | `""`                                            | This id is used as the value for the `exporter` label in all metrics. Useful when your app uses multiple executors and you want to measure them separately                                                    |
| `registry`    | `prometheus_client.CollectorRegistry` | `prometheus_client.REGISTRY` (default registry) | Useful when you're using a registry other than the default for whatever reason, e.g. using `prometheus_client` [multiprocess mode](https://github.com/prometheus/client_python#multiprocess-mode-eg-gunicorn) |

### Custom executors

The `InstrumentedExecutorProxy` class does the heavy-lifting. If you're using a custom executor, you can still instrument them by using wrapping it:

```py
from executor_exporter import InstrumentedExecutorProxy, ExecutorExporter

max_workers = 42
executor = YourCustomExecutor(max_workers)
exporter = ExecutorExporter(executor)

instrumented_executor = InstrumentedExecutorProxy(executor, exporter, max_workers)
```
