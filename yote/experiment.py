"""Saves data corresponding to experiments in a folder."""

from os import PathLike
import logging
import uuid
from pathlib import Path
from collections import namedtuple
from typing import Optional

import orjson

from yote.logger import Logger

Handlers = namedtuple(
    'Handlers', ['file_handler', 'stream_handler']
)


class Experiment(Logger):
    def __init__(
        self,
        _id: Optional[str] = None,
        data_path: str = "yote-out",
        meta: Optional[dict] = None,
        print_every: int = 1,
        verbose: bool = True,
    ):
        self._id = _id or str(uuid.uuid4())
        self.data_path = Path(data_path)
        (self.data_path / Path(self._id)).mkdir(parents=True, exist_ok=True)

        handlers = self._make_log_handlers(
            self.data_path / Path(self._id) / Path("metrics.log")
        )

        super().__init__(
            self._id,
            handlers.file_handler,
            handlers.stream_handler,
            print_every=print_every,
            verbose=verbose
        )

        if meta:
            meta_path = (
                self.data_path / Path(self._id) / Path("meta.json")
            )
            with open(meta_path, "wb") as f:
                f.write(orjson.dumps(meta))

    @classmethod
    def from_id(
        cls,
        _id: str,
        data_path: str = "yote-out",
        print_every: int = 1,
        verbose: bool = True
    ):
        return Experiment(
            _id=_id,
            data_path=data_path,
            print_every=print_every,
            verbose=verbose
        )

    @staticmethod
    def _make_log_handlers(path: PathLike):
        formatter = logging.Formatter("%(message)s")

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)

        fh = logging.FileHandler(path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        return Handlers(fh, ch)
