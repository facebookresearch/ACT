# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from enum import Enum

import pint

from .carbon import Carbon, SourceType
from .units import kg, kWh


# based on https://www.nature.com/articles/s41467-024-54634-y
# nickel-based cathode = NMC (nickel magnesium phosphate)
# lithium iron phosphate = LFP
# The data for LFP spans 54 to 69 kgCO2e kWh−1 (Fig. 3a) so take the average of the range for now
# The data for NMC is 59-115 kg / kWh
class CathodeType:
    """
    Enum representing the type of cathode in a lithium-ion battery.

    Attributes:
        LFP (str): Lithium iron phosphate cathode type.
        NMC (str): Nickel magnesium phosphate cathode type.
    """

    LFP = "LFP"
    NMC = "NMC"


LI_BATTERY_CARBON_PER_KWH = {
    CathodeType.NMC: 87 * kg / kWh,
    CathodeType.LFP: 61.5 * kg / kWh,
}


class BatteryModel:
    """
    A model for estimating carbon emissions from batteries.

    This class provides a method to calculate the estimated carbon emissions from a battery based on its capacity.
    """

    def get_carbon(
        self, capacity: pint.Quantity, btype: CathodeType = CathodeType.NMC
    ) -> Carbon:
        """
        Get the estimated carbon emissions from a battery based on its capacity.

        Args:
            capacity (pint.Quantity): The capacity of the battery in kWh.
            btype (CathodeType): The Li battery cathode type. Defaults to CathodeType.NMC.

        Returns:
            Carbon: The total carbon emissions from the battery fabrication.
        """
        c = Carbon(capacity * LI_BATTERY_CARBON_PER_KWH[btype], SourceType.FABRICATION)
        return c
