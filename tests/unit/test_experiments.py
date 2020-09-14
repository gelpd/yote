import os
import unittest
import tempfile

import orjson

from yote.experiment import Experiment

class TestExperiment(unittest.TestCase):

    def test_experiment_folder_created(self):
        with tempfile.TemporaryDirectory() as td:
            experiment = Experiment(data_path=td)
            self.assertTrue(
                os.path.isdir(
                    os.path.join(
                        td,
                        experiment._id
                    )
                )
            )

    def test_experiment_meta_saves(self):
        with tempfile.TemporaryDirectory() as td:
            meta = {"name": "HAHA", "data": 1}
            experiment = Experiment(meta=meta, data_path=td)
            with open(os.path.join(td, experiment._id, "meta.json"), "r") as f:
                saved_meta = orjson.loads(f.read())
            self.assertEqual(saved_meta, meta)

    def test_lines_get_written(self):
        with tempfile.TemporaryDirectory() as td:
            experiment = Experiment(data_path=td)
            lines = [{"name": "haha", "var": i} for i in range(10)]
            [experiment.emit(line) for line in lines]
            with open(os.path.join(td, experiment._id, "metrics.log"), "r") as f:
                read_lines = [orjson.loads(line.strip()) for line in f.readlines()]
            self.assertEqual(read_lines, lines)
