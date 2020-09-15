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
    ):
        self.name = name
        self.print_every = print_every
        self.verbose = verbose

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        self.ch = stream_handler
        self.fh = file_handler

        self.logger.propagate = False
        self.i = 0

    def __del__(self):
        self.ch.close()
        self.fh.close()

    def emit(self, data: dict) -> None:
        record = logging.LogRecord(
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
        self.i += 1
