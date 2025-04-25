# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import yaml

from .common import ACT_ROOT, DRAMProcess
from .storage_model import StorageModel
from .units import units

DEFAULT_DRAM_CONFIG = f"{ACT_ROOT}/models/dram/dram_hynix.yaml"


class DRAMModel(StorageModel):
    """
    A model for estimating carbon emissions from dynamic random access memory (DRAM).
    Attributes:
        None
    """

    def __init__(self, model_file=DEFAULT_DRAM_CONFIG) -> None:
        """
        Initializes a new instance of the DRAMModel class.
        """
        # Load the DRAM model
        with open(model_file) as f:
            dram_model: dict = yaml.load(f, Loader=yaml.FullLoader)
            dram_model = {DRAMProcess(k): units(v) for k, v in dram_model.items()}
        super().__init__(fab_model=dram_model)
