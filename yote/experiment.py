"""Saves data corresponding to experiments in a folder."""

import logging
from os import PathLike
import uuid
from typing import Optional
from pathlib import Path

import orjson


class Experiment:
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
    ):
        self._id: str = _id or str(uuid.uuid4())
        self.data_path: PathLike = Path(data_path)
        self.formatter: logging.Formatter = formatter or logging.Formatter(
            "%(message)s"
        )
        self.verbose: bool = verbose
        self.print_every: int = print_every
        self.prometheus_metrics: dict = prometheus_metrics or {}
        (self.data_path / Path(self._id)).mkdir(parents=True, exist_ok=True)

        #  Configure logger
        self.logger: logging.Logger = logging.getLogger(self._id)
        self.logger.setLevel(logging.DEBUG)

        self.ch: logging.StreamHandler = stream_handler or self._make_stream_handler(
            self.formatter
        )
        self.fh: logging.FileHandler = file_handler or self._make_file_handler(
            self.data_path / Path(self._id) / Path("metrics.log"), self.formatter
        )
        self.logger.propagate = False
        self.log_idx = 0

        #  Handle meta data
        self.meta_path: PathLike = self.data_path / Path(self._id) / Path("meta.json")

        if meta:
            self.write_meta(meta)
            self.meta = meta

        elif self.meta_path.is_file():
            self.meta = self.read_meta()

    def __del__(self):
        self.ch.close()
        self.fh.close()

    def prometheus_observe(self, data: dict) -> None:
        for key in self.prometheus_metrics.keys():
            if data.get(key):
                self.prometheus_metrics[key].observe(data[key])

    def emit(self, data: dict) -> None:
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

    def write_meta(self, meta: dict):
        with open(self.meta_path, "wb") as f:
            f.write(orjson.dumps(meta))

    def read_meta(self) -> dict:
        with open(self.meta_path, "rb") as f:
            return orjson.loads(f.read())