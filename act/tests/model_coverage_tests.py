# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from ..core.capacitor_model import CapacitorModel, CapacitorType
from ..core.dram_model import DRAMModel
from ..core.hdd_model import HDDModel

from ..core.logic_model import LogicModel
from ..core.ssd_model import SSDModel

from .base_test_case import BaseTestCase
from ..core.common import *
from ..core.units import mm2


class ModelCoverageTests(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_logic_coverage(self):
        """Check that all model values properly load across each parameter range"""

        model = LogicModel()
        valid_processes = [
            LogicProcess.N28,
            LogicProcess.N20,
            LogicProcess.N14,
            LogicProcess.N10,
            LogicProcess.N8,
            LogicProcess.N7,
            LogicProcess.N5,
            LogicProcess.N3,
        ]

        for lp in valid_processes:
            for gpa in AbatementLevel:
                for ci in EnergyLocation:
                    model.get_carbon(
                        logic_process=lp,
                        area=2 * mm2,
                        fab_yield=0.87,
                        gpa=gpa,
                        fab_ci=ci,
                    )
                for ci in EnergySource:
                    model.get_carbon(
                        logic_process=lp,
                        area=2 * mm2,
                        fab_yield=0.87,
                        gpa=gpa,
                        fab_ci=ci,
                    )

    def test_dram_coverage(self):
        """Check that all model values properly load across parameter range"""
        model = DRAMModel()
        for dp in DRAMProcess:
            if dp is DRAMProcess.NA:
                continue
            model.get_carbon(capacity=1 * GB, process=dp)

    def test_ssd_coverage(self):
        """Check that all SSD model values properly run"""
        ssd_model = SSDModel()
        for sp in SSDProcess:
            if sp is SSDProcess.NA:
                continue
            ssd_model.get_carbon(process=sp, capacity=3 * GB)

    def test_hdd_coverage(self):
        model = HDDModel()
        for hp in HDDProcess:
            if hp is HDDProcess.NA:
                continue
            model.get_carbon(process=hp, capacity=1 * GB)

    def test_capacitor_coverage(self):
        model = CapacitorModel()
        for cp in CapacitorType:
            model.get_carbon(ctype=cp, weight=0.03 * g, n_caps=2)
