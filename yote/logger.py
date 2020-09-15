"""Abstracts away logging, adds small functionality like print every."""

import logging
from typing import Optional

import orjson


class Logger:
    def __init__(
        self,
        name: str,
        file_handler: logging.FileHandler,
        stream_handler: logging.StreamHandler,
        print_every: int = 1,
        verbose: bool = True,
        prometheus_metrics: Optional[dict] = None,
    ):
        self.name = name
        self.print_every = print_every
        self.verbose = verbose
        self.prometheus_metrics: dict = prometheus_metrics or {}

        self.logger: logging.Logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        self.ch = stream_handler
        self.fh = file_handler

        self.logger.propagate = False
        self.i = 0

    def __del__(self):
        self.ch.close()
        self.fh.close()

    def prometheus_observe(self, data: dict):
        for key in self.prometheus_metrics.keys():
            if data.get(key):
                self.prometheus_metrics[key].observe(data[key])

    def emit(self, data: dict) -> None:
        record: logging.LogRecord = logging.LogRecord(
            self.name,
            logging.INFO,
            self.name,
            0,
            orjson.dumps(data).decode("utf-8"),
            (),
            None,
        )
        if self.verbose and self.i % self.print_every == 0:
            self.ch.emit(record)

        self.fh.emit(record)
        self.prometheus_observe(data)
        self.i += 1
