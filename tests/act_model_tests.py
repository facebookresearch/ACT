# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import pickle
import time

from act.core.act_model import ACTModel
from act.core.bom import BOM
from act.core.carbon import SourceType
from act.core.processes import DRAMProcess, HDDProcess, LogicProcess, SSDProcess
from act.core.utils.load_yaml_with_macros import load_yaml_with_macros
from act.core.utils.units import g, GB, kg, mm2, mW, TB
from act.tests.base_test_case import BaseTestCase


class ACTModelTests(BaseTestCase):
    """Integration tests over the top level ACT model class"""

    def setUp(self):
        super().setUp()

    def test_default_args(self):
        """Test that the minimal default args work as intended"""
        self.test_args.extend(f"-m {self.boms_dir}/tests/empty.yaml".split())
        self.run_act()

    def test_act_model(self):
        """Basic ACT model coverage and checks"""
        act_model = ACTModel()
        file = f"{self.test_dir}/../boms/tests/test.yaml"

        bom = BOM(
            **load_yaml_with_macros(file),
            file=file,
        )

        carbon = act_model.get_carbon(
            bom=bom,
            op_power=100 * mW,
            duty_cycle=1.0,
        )
        self.assertTrue(carbon.total().check(g))

        mlist = act_model.bom

        # check that the resulting materials list specifications match
        logic_dut = mlist.devices["dut"]
        self.assertEqual(logic_dut.area, 10 * mm2)
        self.assertEqual(logic_dut.fab_yield, 0.87)
        self.assertEqual(logic_dut.process, LogicProcess.N14)

        dram_dut = mlist.devices["dram"]
        self.assertEqual(dram_dut.size, 1 * GB)
        self.assertEqual(dram_dut.fab_yield, 0.9)
        self.assertEqual(dram_dut.process, DRAMProcess.DDR4_10NM)

        ssd_dut = mlist.devices["ssd"]
        self.assertEqual(ssd_dut.size, 2 * TB)
        self.assertEqual(ssd_dut.fab_yield, 0.88)
        self.assertEqual(ssd_dut.process, SSDProcess.NAND_10NM)

        hdd_dut = mlist.devices["hdd"]
        self.assertEqual(hdd_dut.size, 1 * TB)
        self.assertEqual(hdd_dut.fab_yield, 0.92)
        self.assertEqual(hdd_dut.process, HDDProcess.BARRACUDA)

        # check the carbon component composition returns non-zero for components that generate a footprint
        expected_stypes = [
            SourceType.OPERATION,
            SourceType.FABRICATION,
            SourceType.PASSIVES,
        ]
        for stype in expected_stypes:
            self.assertTrue(stype in carbon.carbon_by_type.keys())
            self.assertGreater(carbon.partial(stype), 0 * g)

        # check get_fcarbon_by_device returns formatted results
        fcarbon = act_model.results.get_fcarbon_by_device(kg)
        self.assertIsInstance(fcarbon, dict)
        self.assertGreater(len(fcarbon), 0)
        for dev_name, dev_dict in fcarbon.items():
            self.assertIsInstance(dev_name, str)
            self.assertIsInstance(dev_dict, dict)
            for stype_name, formatted_val in dev_dict.items():
                self.assertIsInstance(stype_name, str)
                self.assertIsInstance(formatted_val, str)
                self.assertIn("kilogram", formatted_val)

    def test_results_record_operating_power(self):
        """The results keep the operating power, not the operating year"""
        act_model = ACTModel()
        file = f"{self.test_dir}/../boms/tests/test.yaml"
        bom = BOM(**load_yaml_with_macros(file), file=file)
        act_model.get_carbon(bom=bom, op_power=250 * mW, op_year=2024)
        self.assertEqual(act_model.results.op_power, 250 * mW)

    def test_act_serializability(self):
        """Enforce that the ACT data structure is serializable to ensure multiprocessing compatibility"""
        if "--no-dashboard" in self.test_args:
            self.test_args.remove("--no-dashboard")
        self.test_args.extend(f"-m {self.boms_dir}/server/mtia/mtia2i.yaml".split())
        act = self.run_act()

        serialized = pickle.dumps(act)
        unserialized = pickle.loads(serialized)

        # spot check some fields to ensure proper loading
        self.assertEqual(act.cl_macros, unserialized.cl_macros)
        self.assertEqual(act.op_power, unserialized.op_power)
        self.assertEqual(act.duty_cycle, unserialized.duty_cycle)

    def test_act_run_time(self):
        """Bound the run time to prevent run time regressions"""
        self.test_args.extend(f"-m {self.boms_dir}/server/mtia/mtia2i.yaml".split())
        start_time = time.time()
        act = self.run_act()
        end_time = time.time()

        elapsed_time = end_time - start_time

        # make sure analysis remains less than 2 seconds to be fast
        self.assertLess(elapsed_time, 2)
