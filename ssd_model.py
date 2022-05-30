
# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import sys

class Fab_SSD():
    def __init__(self, config="nand_10nm", fab_yield=0.875):
        ###############################
        # Carbon per capacity
        ###############################
        with open("ssd/ssd_hynix.json", 'r') as f:
            ssd_config = json.load(f)

        with open("ssd/ssd_seagate.json", 'r') as f:
            ssd_config.update(json.load(f))

        with open("ssd/ssd_western.json", 'r') as f:
            ssd_config.update(json.load(f))

        assert config in ssd_config.keys() and "SSD configuration not found"

        self.fab_yield = fab_yield

        self.carbon_per_gb = ssd_config[config] / self.fab_yield
        self.carbon        = 0
        return

    def get_cpg(self, ):
        return self.carbon_per_gb

    def set_capacity(self, capacity):
        self.capacity = capacity
        self.carbon = self.carbon_per_gb * self.capacity

        return

    def get_carbon(self, ):
        return self.carbon


