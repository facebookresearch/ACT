# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import yaml

from .carbon import Carbon, SourceType
from .common import ACT_ROOT
from .logger import log

from .units import mm2, units

DEFAULT_PCB_MODEL_FILE = f"{ACT_ROOT}/models/materials/pcb.yaml"

INTERPOLATED_AVERAGE_KEY = "cpla"


class PCBModel:
    """
    Basic printed circuit board carbon emissions model by area.

    This class provides a simple model for calculating the carbon emissions of a printed circuit board (PCB)
    based on its area and number of layers.
    """

    def __init__(self, model_file: str = DEFAULT_PCB_MODEL_FILE):
        """
        Initializes the PCBModel instance with a model file.

        Args:
            model_file (str): The path to the model file. Defaults to DEFAULT_PCB_MODEL_FILE.
        """
        with open(model_file) as handle:
            model_data = yaml.load(handle, Loader=yaml.FullLoader)

        self.model = {k: units(v) for k, v in model_data.items()}
        if INTERPOLATED_AVERAGE_KEY in self.model:
            self.interpolated_cpla = self.model[INTERPOLATED_AVERAGE_KEY]
            del self.model[INTERPOLATED_AVERAGE_KEY]
        else:
            log.warn(
                "PCB model does not have a default interpolated average carbon / area / layer. If an unregistered number of layers is provided, the model will throw an error."
            )
            self.interpolated_cpla = None

    def get_carbon(self, area, layers: int):
        """
        Calculates the carbon emissions for a given PCB area and number of layers.

        Args:
            area: The area of the PCB.
            layers (int): The number of layers in the PCB.

        Returns:
            Carbon: The total carbon emissions for the PCB.

        Raises:
            AssertionError: If the area is not in units of area.
        """
        assert area.check(mm2), f"Expected area units for PCB model but got {area}"

        # if the CPA for the number of layers is provided, use it directly
        if layers in self.model:
            cpa = self.model[layers]
        elif self.interpolated_cpla is not None:  # otherwise interpolate
            cpa = self.interpolated_cpla * layers
        else:  # otherwise exit
            log.critical(
                f"No PCB model for number of layers {layers} and not default carbon per area per layer provided. Cannot continue."
            )
            exit(-1)

        c = cpa * area
        return Carbon(c, SourceType.FABRICATION)
