import logging

import orjson


class Logger:
    def __init__(
        self,
        path: str,
        name: str,
        print_every: int = 1,
        verbose: bool = True
    ):
        self.path = path
        self.name = name
        self.print_every = print_every
        self.verbose = verbose

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(message)s")

        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.ch.setFormatter(formatter)

        self.fh = logging.FileHandler(path)
        self.fh.setLevel(logging.DEBUG)
        self.fh.setFormatter(formatter)

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
        if self.verbose:
            if self.i % self.print_every == 0:
                self.ch.emit(record)

        self.fh.emit(record)
        self.i += 1
