# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from enum import Enum

import yaml
from .units import *

from .carbon import Carbon, SourceType
from .common import ACT_ROOT, EnergyLocation
from .utils import load_ci_model


class CapacitorType(Enum):
    """
    Enum representing different types of capacitors.

    Attributes:
        MLCC (str): Multilayer Ceramic Capacitor
        TEC (str): Tantalum Electrolytic Capacitor
        GENERIC (str): Generic Capacitor
    """

    MLCC = "mlcc"
    TEC = "tec"
    GENERIC = "generic"


"""Default weight of a capacitor in grams."""
DEFAULT_CAPACITOR_WEIGHT = 0.03 * g

"""Default carbon emissions per capacitor in grams."""
DEFAULT_CARBON_PER_CAPACITOR = 300 * g

"""Default configuration file for capacitor models."""
DEFAULT_CP_CONFIG = f"{ACT_ROOT}/models/passives/capacitors.yaml"


class CapacitorModel:
    """
    A model for estimating carbon emissions from capacitors.

    Attributes:
        capacitor_model (dict): A dictionary mapping CapacitorType to units of carbon per weight.
        ci_model (dict): A dictionary mapping EnergyLocation to carbon intensity values.
    """

    def __init__(self, model_file=DEFAULT_CP_CONFIG) -> None:
        """
        Initializes a new instance of the CapacitorModel class.
        Loads the capacitor model and carbon intensity model from YAML files.

        Args:
            model_file (str, optional): Capacitor model file to load. Defaults to DEFAULT_CP_CONFIG.
        """
        with open(model_file) as f:
            self.capacitor_model: dict[CapacitorType, pint.Quantity] = {
                CapacitorType(c): units(v)
                for c, v in yaml.load(f, Loader=yaml.FullLoader).items()
            }
        self.ci_model = load_ci_model()

    def get_carbon(
        self,
        ci: EnergyLocation = EnergyLocation.JAPAN,
        ctype: CapacitorType = CapacitorType.GENERIC,
        weight: pint.Quantity = DEFAULT_CAPACITOR_WEIGHT,
        n_caps: int = 1,
    ) -> Carbon:
        """
        Get the carbon emissions cost based on the capacitor type and weight of the capacitor.

        Args:
            ci (EnergyLocation, optional): Carbon intensity per manufacturing energy. Defaults to EnergyLocation.JAPAN.
            ctype (CapacitorType, optional): The capacitor type. Defaults to CapacitorType.GENERIC.
            weight (pint.Quantity, optional): Weight of the capacitor. Defaults to DEFAULT_CAPACITOR_WEIGHT.
            n_caps (int, optional): Number of capacitors. Defaults to 1.

        Returns:
            Carbon: A carbon object that encodes the emissions cost of manufacturing.
        """
        if ctype in self.capacitor_model:
            c = Carbon(
                self.capacitor_model[ctype] * weight * n_caps * self.ci_model[ci],
                SourceType.PASSIVES,
            )
            return c
        else:
            return Carbon(DEFAULT_CARBON_PER_CAPACITOR * n_caps, SourceType.PASSIVES)
