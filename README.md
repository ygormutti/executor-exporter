# executor-exporter
[![codecov](https://codecov.io/gh/ygormutti/executor-exporter/branch/main/graph/badge.svg?token=I9ZGCFTQT9)](https://codecov.io/gh/ygormutti/executor-exporter)
[![CI](https://github.com/ygormutti/executor-exporter/actions/workflows/main.yml/badge.svg)](https://github.com/ygormutti/executor-exporter/actions/workflows/main.yml)

A [Prometheus](https://prometheus.io/) exporter for Python's [`concurrent.futures`](https://docs.python.org/3/library/concurrent.futures.html) executor pools. Supports both `ThreadedPoolExecutor` and `ProcessPoolExecutor`.

![water level ruler photo](docs/water_level_ruler.jpg)

*Public domain photo by Patsy Lynch. [More info](https://commons.wikimedia.org/wiki/File:FEMA_-_40847_-_A_water_level_ruler_in_North_Dakota.jpg)*



project_description

## Install it from PyPI

```bash
pip install executor-exporter
```

## Usage

```py
from project_name import BaseClass
from project_name import base_function

BaseClass().base_method()
base_function()
```

## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
