# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from .base_test_case import BaseTestCase
from ..core.common import *
from ..core.capacitor_model import (
    CapacitorModel,
    CapacitorType,
    DEFAULT_CARBON_PER_CAPACITOR,
)
from ..core.carbon import SourceType
from ..core.units import *
from ..core.battery_model import BatteryModel
from ..core.common import EnergyLocation
from ..core.dram_model import DRAMModel
from ..core.hdd_model import HDDModel
from ..core.materials_model import MaterialsModel
from ..core.pcb_model import PCBModel
from ..core.ssd_model import SSDModel


class ModelUnitTests(BaseTestCase):
    """Unit tests over carbon models"""

    def setUp(self):
        super().setUp()

    def test_logic_model(self):
        """Basic unit to spot check the logic carbon calculation result"""
        fab_yield = 0.943543
        area = 145 * mm2
        result = self.act_model.logic_model.get_carbon(
            fab_yield=fab_yield,
            area=area,
            logic_process=LogicProcess.N10,
            n_ics=1,
            gpa=self.gpa,
            fab_ci=self.fab_ci,
        )

        # ensure manually calculated value is correct
        expected = (
            1.475 * kWh / cm2 * area * 583 * g / kWh
            + 240 * g / cm2 * area
            + 500 * g / cm2 * area
        ) / fab_yield + 150 * g
        self.assertEqual(
            set(result.types()), {SourceType.FABRICATION, SourceType.PACKAGING}
        )
        self.assertAlmostEqual(result.partial(SourceType.PACKAGING), 150 * g)
        self.assertAlmostEqual(result.total(), expected)

    def test_storage_models(self):
        """Basic unit tests over storage models"""

        dram_model = DRAMModel()
        ssd_model = SSDModel()
        hdd_model = HDDModel()
        fab_yield = 0.9
        n_ics = 2

        capacity = 10 * GB
        common_args = dict(capacity=capacity, n_ics=n_ics, fab_yield=fab_yield)
        expected_ctypes = {SourceType.FABRICATION, SourceType.PACKAGING}
        pkg_partial = 150 * g * n_ics

        def _check_results(result, expected):
            self.assertAlmostEqual(result.total(), expected)
            self.assertEqual(set(result.types()), expected_ctypes)
            self.assertAlmostEqual(result.partial(SourceType.PACKAGING), pkg_partial)

        # test DRAM model
        result = dram_model.get_carbon(DRAMProcess.DDR3_30NM, **common_args)
        expected = (230 * g / GB * capacity / fab_yield) + 150 * g * n_ics
        _check_results(result, expected)

        # test SSD model
        result = ssd_model.get_carbon(SSDProcess.NAND_30NM, **common_args)
        expected = (31 * g / GB * capacity / fab_yield) + 150 * g * n_ics
        _check_results(result, expected)

        # test HDD model
        result = hdd_model.get_carbon(HDDProcess.BARRACUDA, **common_args)
        expected = (4.57 * g / GB * capacity / fab_yield) + 150 * g * n_ics
        _check_results(result, expected)

    def test_op_model(self):
        """Basic unit test over operational carbon model"""
        lifetime = 3.5 * year
        duty_cycle = 0.723
        op_power = 273 * mW
        op_ci = EnergyLocation.AUSTRALIA

        op_carbon = self.act_model.op_model.get_carbon(
            lifetime=lifetime, duty_cycle=duty_cycle, op_power=op_power, op_ci=op_ci
        )

        # manually calculate expected
        expected = 597 * g / kWh * op_power * duty_cycle * lifetime
        self.assertEqual(op_carbon.types(), [SourceType.OPERATION])
        self.assertAlmostEqual(expected, op_carbon.total())

    def test_capacitor_model(self):
        model = CapacitorModel()
        ci = EnergyLocation.JAPAN
        ctype = CapacitorType.GENERIC
        weight = 1.0 * kg
        n_caps = 2

        # test the generic capacitor model
        carbon = model.get_carbon(ci=ci, ctype=ctype, weight=weight, n_caps=n_caps)
        expected_carbon = DEFAULT_CARBON_PER_CAPACITOR * n_caps
        self.assertEqual(carbon.total(), expected_carbon)
        self.assertEqual(carbon.types(), [SourceType.PASSIVES])

        # test the MLCC model
        carbon = model.get_carbon(
            ci=ci, ctype=CapacitorType.MLCC, weight=weight, n_caps=n_caps
        )
        expected_carbon = 6862 * MJ / kg * weight * 485 * g / kWh * n_caps
        self.assertAlmostEqual(carbon.total(), expected_carbon)
        self.assertEqual(carbon.types(), [SourceType.PASSIVES])

        # test the TEC model
        carbon = model.get_carbon(
            ci=ci,
            ctype=CapacitorType.TEC,
            weight=weight,
            n_caps=n_caps,
        )
        expected_carbon = 5567 * MJ / kg * weight * 485 * g / kWh * n_caps
        self.assertAlmostEqual(carbon.total(), expected_carbon)
        self.assertEqual(carbon.types(), [SourceType.PASSIVES])

    def test_materials_model(self):
        """Basic materials model test"""
        model = MaterialsModel()

        mat = model.MaterialType.STEEL
        weight = 0.25 * kg
        carbon = model.get_carbon(mat=mat, weight=weight)
        expected_carbon = weight * 1.89  # manually calculate
        self.assertAlmostEqual(expected_carbon, carbon.total())
        self.assertEqual(carbon.types(), [SourceType.ENCLOSURE])

    def test_battery_model(self):
        """Basic battery model test"""
        model = BatteryModel()
        capacity = 1000 * mWh
        carbon = model.get_carbon(capacity=capacity)
        expected_carbon = 87 * kg / kWh * capacity
        self.assertAlmostEqual(expected_carbon, carbon.total())
        self.assertEqual(carbon.types(), [SourceType.FABRICATION])

    def test_pcb_model(self):
        """Basic PCB model test"""
        model = PCBModel()

        # test a case where the value exists in the file
        area = 1.5 * cm2
        layers = 4
        result = model.get_carbon(area=area, layers=layers)
        expected = 0.43 * kg / m2 * area
        self.assertAlmostEqual(result.total(), expected)
        self.assertEqual(result.types(), [SourceType.FABRICATION])

        # test an interpolated test case
        area = 2.5 * cm2
        layers = 7
        result = model.get_carbon(area=area, layers=layers)
        expected = 0.13 * kg / m2 * layers * area
        self.assertAlmostEqual(result.total(), expected)
        self.assertEqual(result.types(), [SourceType.FABRICATION])
