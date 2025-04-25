# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from ..core.common import *
from ..core.dram_model import DRAMModel
from ..core.hdd_model import HDDModel
from ..core.logic_model import LogicModel
from ..core.materials_model import MaterialsModel
from ..core.ssd_model import SSDModel

from .base_test_case import BaseTestCase
from ..core.units import *
from ..core.carbon import Carbon, SourceType


class BasicACTTests(BaseTestCase):
    """Ensures that the original ACT functionality is preserved based on the input/output pairs"""

    def test_default_logic_model(self):
        """Ensure that the default ACT model logic results are preserved"""
        logic_model = LogicModel()

        tp = LogicProcess.N14
        self.assertAlmostEqual(
            logic_model.get_cpa(logic_process=tp),
            1556.685714285714 * g / cm2,
        )
        self.assertEqual(
            logic_model.get_carbon_energy(logic_process=tp),
            699.6 * g / cm2,
        )
        self.assertEqual(logic_model.get_carbon_gas(logic_process=tp), 162.5 * g / cm2)
        self.assertEqual(logic_model.get_carbon_materials(tp), 500 * g / cm2)

    def test_logic_model_integration(self):
        """Ensure that the default configuration that is fed by default to ACT does not change"""
        tp = LogicProcess.N10
        gpa = AbatementLevel.GPA95
        fab_ci = EnergySource.COAL
        logic_model = LogicModel()

        self.assertEqual(
            logic_model.get_cpa(gpa=gpa, fab_ci=fab_ci, logic_process=tp),
            2228.0 * g / cm2,
        )
        self.assertEqual(
            logic_model.get_carbon_energy(fab_ci=fab_ci, logic_process=tp),
            1209.5 * g / cm2,
        )
        self.assertEqual(
            logic_model.get_carbon_gas(gpa=gpa, logic_process=tp), 240 * g / cm2
        )
        self.assertEqual(logic_model.get_carbon_materials(tp), 500 * g / cm2)

    def test_basic_dram_model(self):
        """Ensure original DRAM model results remain consistent"""
        dram_model = DRAMModel()
        tp = DRAMProcess.DDR4_10NM
        carbon_cost = dram_model.get_carbon(process=tp, capacity=3 * GB)

        self.assertEqual(carbon_cost.total(), 222.8571428571429 * g)

    def test_basic_hdd_model(self):
        """Ensure original HDD model results remain consistent"""
        hdd_model = HDDModel()
        hp = HDDProcess.BARRACUDA
        capacity = 3 * GB
        fab_yield = 1.0  # the original model doesn't properly account for yield

        carbon_cost = hdd_model.get_carbon(hp, capacity, fab_yield)
        cpg = hdd_model.get_cpg(
            hp, fab_yield
        )  # the original HDD model doesn't have a yield

        self.assertAlmostEqual(cpg, 4.57 * g / GB)
        self.assertAlmostEqual(carbon_cost.total(), 13.71 * g)

    def test_basic_ssd_model(self):
        """Ensure SSD model loads and runs correctly"""
        fab_yield = 0.9
        ssd_model = SSDModel()
        ssd_process = SSDProcess.NAND_10NM

        ssd_carbon = ssd_model.get_carbon(
            process=ssd_process, capacity=3 * GB, fab_yield=fab_yield
        )
        ssd_cpg = ssd_model.get_cpg(process=ssd_process, fab_yield=fab_yield)
        self.assertAlmostEqual(ssd_cpg, 10 * g / GB / fab_yield)
        self.assertAlmostEqual(ssd_carbon.total(), 30 * g / fab_yield)

    def test_basic_materials_model(self):
        """Basic coverage over materials model"""
        model = MaterialsModel()
        for m in model.MaterialType:
            if m is not model.MaterialType.NA:
                c = model.get_carbon(m, 100 * g)
                self.assertTrue(SourceType.ENCLOSURE in c.carbon_by_type.keys())

    def test_carbon_result(self):
        """Coverage over carbon component tracking results"""
        x = Carbon(100 * g, SourceType.FABRICATION)
        y = Carbon(50 * g, SourceType.MATERIALS)
        z = Carbon(75 * g, SourceType.OPERATION)
        w = Carbon(32 * g, SourceType.MATERIALS)

        # check add operation over results
        radd = w + y
        self.assertEqual(radd.total(), 82 * g)

        # check subtract operation over results
        rsub = y - w
        self.assertEqual(rsub.total(), 18 * g)

        # check component partials
        wxyz = w + x + y + z
        self.assertEqual(wxyz.total(), 257 * g)
        self.assertEqual(wxyz.partial(SourceType.FABRICATION), 100 * g)
        self.assertEqual(wxyz.partial(SourceType.MATERIALS), 82 * g)
        self.assertEqual(wxyz.partial(SourceType.OPERATION), 75 * g)
        self.assertEqual(wxyz.partial(SourceType.PACKAGING), 0 * g)
