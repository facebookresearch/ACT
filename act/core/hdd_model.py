# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import yaml
from .units import *

from .common import ACT_ROOT, HDDProcess
from .storage_model import StorageModel

DEFAULT_HDD_CONFIG = [
    f"{ACT_ROOT}/models/hdd/hdd_consumer.yaml",
    f"{ACT_ROOT}/models/hdd/hdd_enterprise.yaml",
]


class HDDModel(StorageModel):
    """
    A model for estimating carbon emissions from hard disk drives (HDDs).

    Attributes:
        None
    """

    def __init__(self, model_files=DEFAULT_HDD_CONFIG) -> None:
        """
        Initializes a new instance of the HDDModel class.

        Loads the HDD carbon cost models from YAML files.

        Args:
            model_files (list): A list of file paths to the HDD carbon cost models.
        """

        # Load the HDD carbon cost models
        hdd_model = dict()
        for mfile in model_files:
            with open(mfile) as f:
                model_data = yaml.load(f, Loader=yaml.FullLoader)
                hdd_model.update(model_data)

        hdd_model = {HDDProcess(k): units(v) for k, v in hdd_model.items()}
        super().__init__(fab_model=hdd_model)
