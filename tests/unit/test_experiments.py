import io
import os
import sys
import unittest
import tempfile

import orjson

from yote.experiment import Experiment


def capture_output(experiment):
    experiment.ch.stream = io.StringIO()


def get_output(experiment):
    experiment.ch.stream.seek(0)
    return experiment.ch.stream.readlines()


class TestExperiment(unittest.TestCase):
    def test_experiment_folder_created(self):
        with tempfile.TemporaryDirectory() as td:
            experiment = Experiment(data_path=td)
            self.assertTrue(os.path.isdir(os.path.join(td, experiment._id)))

    def test_experiment_meta_saves(self):
        with tempfile.TemporaryDirectory() as td:
            meta = {"name": "HAHA", "data": 1}
            experiment = Experiment(meta=meta, data_path=td)
            with open(os.path.join(td, experiment._id, "meta.json"), "r") as f:
                saved_meta = orjson.loads(f.read())
            self.assertEqual(saved_meta, meta)

    def test_lines_get_printed(self):
        with tempfile.TemporaryDirectory() as td:
            experiment = Experiment(data_path=td)
            capture_output(experiment)
            lines = [{"name": "haha", "var": i} for i in range(10)]
            [experiment.emit(line) for line in lines]
            read_lines = [orjson.loads(x) for x in get_output(experiment)]
            self.assertEqual(read_lines, lines)

    def test_lines_get_written(self):
        with tempfile.TemporaryDirectory() as td:
            experiment = Experiment(data_path=td)
            capture_output(experiment)
            lines = [{"name": "haha", "var": i} for i in range(10)]
            [experiment.emit(line) for line in lines]
            with open(os.path.join(td, experiment._id, "metrics.log"), "r") as f:
                read_lines = [orjson.loads(line.strip()) for line in f.readlines()]
            self.assertEqual(read_lines, lines)

    def test_lines_print_every_n(self):
        with tempfile.TemporaryDirectory() as td:
            experiment = Experiment(data_path=td, print_every=5)
            capture_output(experiment)
            lines = [{"name": "haha", "var": i} for i in range(10)]
            [experiment.emit(line) for line in lines]
            read_lines = [orjson.loads(x) for x in get_output(experiment)]
            self.assertEqual([lines[0], lines[5]], read_lines)

    def test_verbose_suppress(self):
        with tempfile.TemporaryDirectory() as td:
            experiment = Experiment(data_path=td, verbose=False)
            capture_output(experiment)
            lines = [{"name": "haha", "var": i} for i in range(10)]
            [experiment.emit(line) for line in lines]
            read_lines = [orjson.loads(x) for x in get_output(experiment)]
            self.assertEqual(read_lines, [])

    def test_experiment_from_id(self):
        with tempfile.TemporaryDirectory() as td:
            meta = {"asdf": "test"}
            experiment = Experiment(data_path=td, verbose=False, meta=meta)
            _id = experiment._id
            experiment = Experiment.from_id(_id, data_path=td)
            self.assertEqual(experiment.meta, meta)
