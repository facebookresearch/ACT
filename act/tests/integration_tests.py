# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from ..core.common import CARBON_PER_IC_PACKAGE
from ..core.units import kg

from .base_test_case import BaseTestCase


class IntegrationTest(BaseTestCase):
    def setUp(self):
        super().setUp()

    def _filtered_total(self, prefix, results):
        total = 0 * kg
        entries = 0
        for sname, carbon in results.items():
            if sname.startswith(prefix):
                total += carbon.total()
                entries += 1
        return total

    def test_dellr740(self):
        """Ensure that the dell R740 results preserve the original ACT model results as closely as possible"""
        self.test_args.extend(f"-m {self.boms_dir}/dellr740.yaml".split())
        act = self.run_act()

        silicon_results = act.silicon_results
        cpu_total = self._filtered_total("cpu", silicon_results)
        ssd_secondary_total = self._filtered_total("ssd.secondary", silicon_results)
        ssd_main_total = self._filtered_total("ssd.main", silicon_results)
        dram_total = self._filtered_total("dram.main", silicon_results)

        # check CPU carbon emissions total
        # weak bound due to some possible floating point error between the original and updated
        self.assertAlmostEqual(cpu_total, 23.143405714285716 * kg, places=0)

        # the amount emitted in the original model does not include DRAM IC packaging (n = 19)
        self.assertAlmostEqual(
            ssd_secondary_total, 62.75 * kg + 19 * CARBON_PER_IC_PACKAGE
        )

        # check that the per SSD costs are the same as in the original per SSD
        self.assertAlmostEqual(ssd_main_total, 8 * (136.0457142857143 + 1.95) * kg)

        # check DRAM costs total
        self.assertAlmostEqual(dram_total, 330.4285714285714 * kg)

    def test_fairphone3(self):
        """Ensure that the fairphone3 model aligns with the original results as closely as possible to ensure no regression"""
        self.test_args.extend(f"-m {self.boms_dir}/fairphone3.yaml".split())
        act = self.run_act()

        silicon_results = act.silicon_results

        # ensure expected number of devices appear
        self.assertEqual(len(silicon_results), 23)
        dram_flash_carbon = (
            silicon_results["dram"].total() + silicon_results["ssd"].total()
        )
        self.assertAlmostEqual(dram_flash_carbon, 5.310285714285714 * kg)

        cpu_carbon = silicon_results["cpu"].total()
        self.assertAlmostEqual(cpu_carbon, 0.8992937142857143 * kg)

        ic_carbon = self._filtered_total("ics", silicon_results)
        self.assertAlmostEqual(ic_carbon, 5.691643885714286 * kg)

    def test_bom_import(self):
        """Test that importing a file works as expected"""
        self.test_args.extend(f"-m {self.boms_dir}/test.yaml".split())
        act = self.run_act()

        # ensure the imported devices appear in the result
        self.assertTrue("subsystem.imported_cap" in act.passives_results)
        self.assertTrue("subsystem.imported_si" in act.silicon_results)
        self.assertTrue("subsystem.imported_mat" in act.materials_results)
