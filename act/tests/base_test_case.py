# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import os

import sys
import tempfile
import unittest
from unittest.mock import patch

from ..act_model import main

from ..core.logger import setup_logger
from ..core.common import *
import warnings

from ..act_model import ACTModel

warnings.simplefilter("ignore", ResourceWarning)


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # temp_dir for tests
        self.temp_dir = tempfile.TemporaryDirectory(prefix="act_out_")
        self.out_dir = self.temp_dir.name

        self.test_dir = os.path.abspath(os.path.dirname(__file__))
        self.test_args = ["./act"]
        self.boms_dir = f"{self.test_dir}/../boms/"

        self.gpa = AbatementLevel.GPA95
        self.fab_ci = EnergyLocation.TAIWAN
        self.act_model = ACTModel()

        setup_logger(loglevel=logging.INFO)

    def run_act(self, loglevel=logging.INFO):
        setup_logger(loglevel=loglevel)
        with patch.object(sys, "argv", self.test_args):
            return main()
