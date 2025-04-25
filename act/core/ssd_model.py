# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import yaml

from .common import ACT_ROOT, SSDProcess
from .storage_model import StorageModel
from .units import units


class SSDModel(StorageModel):
    """
    A model for calculating SSD-related carbon emissions.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the SSDModel class.
        """
        # Load the SSD storage model configuration
        with open(f"{ACT_ROOT}/models/ssd/ssd_hynix.yaml", "r") as f:
            ssd_model: dict[SSDProcess, units] = {
                SSDProcess(k): units(v)
                for k, v in yaml.load(f, Loader=yaml.FullLoader).items()
            }
        with open(f"{ACT_ROOT}/models/ssd/ssd_seagate.yaml", "r") as f:
            ssd_model.update(
                {
                    SSDProcess(k): units(v)
                    for k, v in yaml.load(f, Loader=yaml.FullLoader).items()
                }
            )
        with open(f"{ACT_ROOT}/models/ssd/ssd_western.yaml", "r") as f:
            ssd_model.update(
                {
                    SSDProcess(k): units(v)
                    for k, v in yaml.load(f, Loader=yaml.FullLoader).items()
                }
            )
        super().__init__(fab_model=ssd_model)
