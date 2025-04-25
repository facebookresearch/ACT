# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from ..core.utils import *
from ..core.units import mm2


class UtilsTests:
    def setUp(self):
        super().setUp()

    def test_yield_models(self):
        # spot check that the yield models don't emit results outside of 0 to 1 and put in coverage
        areas = [1 * mm2, 10 * mm2, 100 * mm2, 1000 * mm2, 10000 * mm2]
        densities = [1 / mm2, 10 / mm2, 100 / mm2, 1000 / mm2, 10000 / mm2]

        for a in areas:
            for d in densities:
                p = poisson_model(area=a, density=d)
                self.assertTrue(0 <= p <= 1)
                mt = murphy_model(area=a, density=d, dist="triangle")
                self.assertTrue(0 <= mt <= 1)
                mr = murphy_model(area=a, density=d, dist="rect")
                self.assertTrue(0 <= mr <= 1)
                e = exponential_model(area=a, density=d)
                self.assertTrue(0 <= e <= 1)
