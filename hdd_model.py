
# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import sys, os
from pathlib import Path

class Fab_HDD():
    def __init__(self, config="BarraCuda"):
        ###############################
        # Carbon per capacity
        ###############################
        ACT_dir = Path(__file__).parent.absolute()
        with open(os.path.join(ACT_dir,"hdd/hdd_consumer.json"), 'r') as f:
            hdd_config = json.load(f)

        with open(os.path.join(ACT_dir,"hdd/hdd_enterprise.json"), 'r') as f:
            hdd_config.update(json.load(f))

        assert config in hdd_config.keys() and "HDD configuration not found"

        self.carbon_per_gb = hdd_config[config]
        self.carbon        = 0
        return

    def get_cpg(self, ):
        return self.carbon_per_gb

    def set_capacity(self, capacity):
        self.capacity = capacity
        self.carbon = carbon_per_gb

        return

    def get_carbon(self, ):
        return self.carbon

