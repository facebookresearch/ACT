
# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import sys

class Fab_DRAM():
    def __init__(self,  config = "ddr4_10nm", fab_yield=0.875):

        ###############################
        # Carbon per capacity
        ###############################
        with open("dram/dram_hynix.json", 'r') as f:
            dram_config = json.load(f)

        assert config in dram_config.keys() and "DRAM configuration not found"

        self.fab_yield = fab_yield

        self.carbon_per_gb = dram_config[config] / self.fab_yield
        self.carbon        = 0

    def get_cpg(self, ):
        return self.carbon_per_gb

    def set_capacity(self, capacity):
        self.capacity = capacity
        self.carbon = self.carbon_per_gb * self.capacity

        return

    def get_carbon(self, ):
        return self.carbon

