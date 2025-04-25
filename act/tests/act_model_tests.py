# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from ..act_model import ACTModel
from ..core.carbon import SourceType
from ..core.common import *

from .base_test_case import BaseTestCase
from ..core.units import *
import copy
import glob

import yaml

from ..core.bom import BOM

from ..core.logger import log


class ACTModelTests(BaseTestCase):
    """Integration tests over the top level ACT model class"""

    def setUp(self):
        super().setUp()

    def test_act_model(self):
        """Basic ACT model coverage and checks"""
        act_model = ACTModel()
        file = f"{self.test_dir}/../boms/test.yaml"
        with open(file) as handle:
            bom = BOM(
                **yaml.load(handle, Loader=yaml.FullLoader),
                file=file,
                material_type=act_model.materials_model.MaterialType,
            )

        carbon = act_model.get_carbon(
            bom=bom,
            op_power=100 * mW,
            duty_cycle=1.0,
        )
        self.assertTrue(carbon.total().check(g))

        mlist = act_model.last_bom

        # check that the resulting materials list specifications match
        logic_dut = mlist.silicon["dut"]
        self.assertEqual(logic_dut.area, 10 * mm2)
        self.assertEqual(logic_dut.fab_yield, 0.87)
        self.assertEqual(logic_dut.process, LogicProcess.N14)

        dram_dut = mlist.silicon["dram"]
        self.assertEqual(dram_dut.capacity, 1 * GB)
        self.assertEqual(dram_dut.fab_yield, 0.9)
        self.assertEqual(dram_dut.process, DRAMProcess.DDR4_10NM)

        ssd_dut = mlist.silicon["ssd"]
        self.assertEqual(ssd_dut.capacity, 2 * TB)
        self.assertEqual(ssd_dut.fab_yield, 0.88)
        self.assertEqual(ssd_dut.process, SSDProcess.NAND_10NM)

        hdd_dut = mlist.silicon["hdd"]
        self.assertEqual(hdd_dut.capacity, 1 * TB)
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

    def test_default_args(self):
        """Test that the minimal default args work as intended"""
        self.run_act()

    def test_cl_args(self):
        """Coverage over basic command line argument run of ACT"""
        self.test_args.extend(
            f"--logic-area 145mm2 --dram-size 1GB --ssd-size 2TB --hdd-size 4TB --duty-cycle 0.7 --lifetime 2years --fab-ci taiwan --cap-ci korea --op-ci usa --logic-process 14 --dram-process ddr4_10nm --ssd-process nand_10nm --hdd-process BarraCuda --loglevel info --gpa 99 --logic-yield 0.9 --dram-yield 0.85 --ssd-yield 0.89 --hdd-yield 0.95 --op-power 100mW --ics 1 --caps 1  --pcb-area 100mm2 --export-file {self.out_dir}/test_result.yaml".split()
        )
        self.run_act()

    def test_bom_coverage_test(self):
        """Glob and test all materials files in the BOM directory"""
        boms = glob.glob(f"{self.test_dir}/../boms/**/*.yaml", recursive=True)
        self.assertGreater(len(boms), 0)  # make sure at least one is detected

        base_args = copy.deepcopy(self.test_args)
        for bom in boms:
            log.info(f"Testing {bom}...")
            self.test_args = copy.deepcopy(base_args)
            self.test_args.extend(f"-m {bom}".split())
            self.run_act()
