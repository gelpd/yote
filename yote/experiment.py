"""Saves data corresponding to experiments in a folder."""

import logging
from os import PathLike
import uuid
from typing import Optional, Tuple
from pathlib import Path

import orjson


class Experiment:
    """Write metrics to stdout and a file (and optionally, prometheus).

    Using the emit function, you can:
        - Save metrics to a file
        - Potentially print them (every n lines)
        - Execute callbacks on the data you emit
        - Make prometheus observations

    """

    def __init__(
        self,
        _id: Optional[str] = None,
        data_path: str = "yote-out",
        meta: Optional[dict] = None,
        print_every: int = 1,
        verbose: bool = True,
        file_handler: Optional[logging.FileHandler] = None,
        stream_handler: Optional[logging.StreamHandler] = None,
        formatter: Optional[logging.Formatter] = None,
        prometheus_metrics: Optional[dict] = None,
        do_every: Optional[dict] = None,
    ):
        """Set defaults, create directories if needed, save meta-data."""
        self._id: str = _id or str(uuid.uuid4())
        self.data_path: PathLike = Path(data_path)
        self.verbose: bool = verbose
        self.print_every: int = print_every
        self.prometheus_metrics: dict = prometheus_metrics or {}
        self.do_every: dict = do_every or {}

        (self.data_path / Path(self._id)).mkdir(parents=True, exist_ok=True)

        self.ch, self.fh = self._setup_logger(
            formatter=formatter,
            stream_handler=stream_handler,
            file_handler=file_handler,
        )

        self.meta = self._setup_meta(meta)

        #  log_idx is used for print_every and do_every
        self.log_idx = 0

    def __del__(self):
        """Close stream and file handles."""
        self.ch.close()
        self.fh.close()

    def _setup_logger(
        self,
        formatter: Optional[logging.Formatter] = None,
        stream_handler: Optional[logging.StreamHandler] = None,
        file_handler: Optional[logging.FileHandler] = None,
    ) -> Tuple[logging.StreamHandler, logging.FileHandler]:
        """Configure a logger for the experiment.

        We create a stream handle whether or not a user wants
        it. Writing to a file is not optional in this code so
        we create a FileHandler.

        The logger does not propagate up the chain so as to
        not be very invasive wrt your existing logging setup.

        """
        logger: logging.Logger = logging.getLogger(self._id)
        logger.setLevel(logging.DEBUG)

        log_formatter: logging.Formatter = formatter or logging.Formatter("%(message)s")

        ch: logging.StreamHandler = stream_handler or self._make_stream_handler(
            log_formatter
        )
        fh: logging.FileHandler = file_handler or self._make_file_handler(
            self.data_path / Path(self._id) / Path("metrics.log"), log_formatter
        )

        logger.propagate = False

        return ch, fh

    def _setup_meta(self, meta: Optional[dict] = None) -> dict:
        """Write or read meta data for the experiment.

        When you instantiate an experiment with meta data,
        we will write it to a file. When you use the builder
        pattern to load an existing experiment, we will read
        the meta.
        """
        meta_path: PathLike = self.data_path / Path(self._id) / Path("meta.json")

        if meta:
            self.write_meta(meta, meta_path)
            return meta
        elif meta_path.is_file():
            return self.read_meta(meta_path)

        return {}

    def prometheus_observe(self, data: dict) -> None:
        """Allows users to set prometheus metrics to observe.

        Users can supply a prometheus_metrics dict when
        creating an experiment. This dictionary should have
        keys corresponding to keys in the data they log.
        The values should be prometheus client metrics which
        have an observe method.
        """
        for key in self.prometheus_metrics.keys():
            if data.get(key):
                self.prometheus_metrics[key].observe(data[key])

    def emit(self, data: dict) -> None:
        """Create and write a log record.

        A log record is written to a metrics file and
        optionally written to stdout. Additionally,
        metrics can be emitted for prometheus and user
        supplied callbacks will be called.
        """
        record: logging.LogRecord = logging.LogRecord(
            self._id,
            logging.INFO,
            self._id,
            0,
            orjson.dumps(data).decode("utf-8"),
            (),
            None,
        )

        if self.verbose and self.log_idx % self.print_every == 0:
            self.ch.emit(record)

        for fun, freq in self.do_every.items():
            if self.log_idx % freq == 0:
                fun(data)

        self.fh.emit(record)
        self.prometheus_observe(data)
        self.log_idx += 1

    @classmethod
    def from_id(
        cls,
        _id: str,
        data_path: str = "yote-out",
        print_every: int = 1,
        verbose: bool = True,
    ):
        """Create an experiment class from an existing path."""
        return cls(
            _id=_id, data_path=data_path, print_every=print_every, verbose=verbose
        )

    @staticmethod
    def _make_file_handler(
        path: PathLike, formatter: logging.Formatter
    ) -> logging.FileHandler:
        fh: logging.FileHandler = logging.FileHandler(path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        return fh

    @staticmethod
    def _make_stream_handler(formatter: logging.Formatter) -> logging.StreamHandler:
        ch: logging.StreamHandler = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        return ch

    @staticmethod
    def write_meta(meta: dict, path: PathLike):
        with open(path, "wb") as f:
            f.write(orjson.dumps(meta))

    @staticmethod
    def read_meta(path: PathLike) -> dict:
        with open(path, "rb") as f:
            return orjson.loads(f.read())
