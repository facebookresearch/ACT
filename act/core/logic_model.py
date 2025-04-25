# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import pint
import yaml

from .carbon import Carbon, SourceType

from .common import (
    AbatementLevel,
    ACT_ROOT,
    CARBON_PER_IC_PACKAGE,
    DEFAULT_FAB_YIELD,
    EnergyLocation,
    LogicProcess,
)
from .logger import log
from .units import mm2, units
from .utils import load_ci_model

DEFAULT_EPA_CONFIG = f"{ACT_ROOT}/models/logic/epa.yaml"
DEFAULT_MATERIALS_CONFIG = f"{ACT_ROOT}/models/logic/materials.yaml"
DEFAULT_GPA95_CONFIG = f"{ACT_ROOT}/models/logic/gpa_95.yaml"
DEFAULT_GPA99_CONFIG = f"{ACT_ROOT}/models/logic/gpa_99.yaml"


class LogicModel:
    """
    A class representing a logic model for calculating carbon emissions.

    Attributes:
        epa_model (dict): A dictionary mapping logic processes to energy per unit area.
        materials_model (dict): A dictionary mapping logic processes to raw materials per unit area.
        gpa_model (dict): A dictionary mapping abatement levels to dictionaries of logic processes to gas emissions per unit area.
        ci_model (dict): A dictionary mapping energy locations to carbon intensity models.
    """

    def __init__(
        self,
        epa_file=DEFAULT_EPA_CONFIG,
        materials_config=DEFAULT_MATERIALS_CONFIG,
        gpa95_file=DEFAULT_GPA95_CONFIG,
        gpa99_file=DEFAULT_GPA99_CONFIG,
    ) -> None:
        """
        Initializes a LogicModel instance.

        Args:
            epa_file (str, optional): The path to the EPA configuration file. Defaults to DEFAULT_EPA_CONFIG.
            materials_config (str, optional): The path to the materials configuration file. Defaults to DEFAULT_MATERIALS_CONFIG.
            gpa95_file (str, optional): The path to the GPA 95 configuration file. Defaults to DEFAULT_GPA95_CONFIG.
            gpa99_file (str, optional): The path to the GPA 99 configuration file. Defaults to DEFAULT_GPA99_CONFIG.
        """
        # energy per unit area
        with open(epa_file) as f:
            self.epa_model = {
                LogicProcess(k): units(v)
                for k, v in yaml.load(f, Loader=yaml.FullLoader).items()
            }

        # raw materials per unit area
        with open(materials_config) as f:
            self.materials_model = {
                LogicProcess(k): units(v)
                for k, v in yaml.load(f, Loader=yaml.FullLoader).items()
            }

        self.gpa_model = dict()
        with open(gpa95_file) as f:
            self.gpa_model[AbatementLevel.GPA95] = {
                LogicProcess(k): units(v)
                for k, v in yaml.load(f, Loader=yaml.FullLoader).items()
            }
        with open(gpa99_file) as f:
            self.gpa_model[AbatementLevel.GPA99] = {
                LogicProcess(k): units(v)
                for k, v in yaml.load(f, Loader=yaml.FullLoader).items()
            }
        self.gpa_model[AbatementLevel.GPA97] = {
            key: (
                self.gpa_model[AbatementLevel.GPA95][key]
                + self.gpa_model[AbatementLevel.GPA99][key]
            )
            / 2.0
            for key in self.gpa_model[AbatementLevel.GPA95].keys()
        }

        # load the carbon intensity model by source/location
        self.ci_model = load_ci_model()

    def get_cpa(
        self,
        logic_process: LogicProcess,
        fab_yield: float = DEFAULT_FAB_YIELD,
        gpa=AbatementLevel.GPA97,
        fab_ci=EnergyLocation.TAIWAN,
    ) -> pint.Quantity:
        """
        Get the carbon per area for a given logic process and fabrication yield.

        Args:
            logic_process (LogicProcess): The logic process to calculate carbon per area for.
            fab_yield (float, optional): The fabrication yield. Defaults to DEFAULT_FAB_YIELD.
            gpa (AbatementLevel): Manufacturing gas abatement level. Defaults to AbatementLevel.GPA97.
            fab_ci (EnergyLocation): Carbon intensity of logic manufacturing. Defaults to EnergyLocation.TAIWAN.

        Returns:
            pint.Quantity: The carbon per area.

        Raises:
            SystemExit: If the carbon intensity or abatement level is not recognized.
        """
        if fab_ci not in self.ci_model:
            log.error(
                f"Error: Carbon intensity must either be loc | src dependent. Got {fab_ci}"
            )
            exit(-1)
        if gpa not in AbatementLevel:
            log.error(f"Abatement level {gpa} not recognized...")
            exit(-1)

        fab_ci = self.ci_model[fab_ci]

        carbon_energy = fab_ci * self.epa_model[logic_process]
        carbon_gas = self.gpa_model[gpa][logic_process]
        carbon_materials = self.materials_model[logic_process]

        carbon_per_area = carbon_energy + carbon_gas + carbon_materials
        carbon_per_area = carbon_per_area / fab_yield

        return carbon_per_area

    def get_carbon(
        self,
        logic_process: LogicProcess,
        area: pint.Quantity,
        fab_yield: float = DEFAULT_FAB_YIELD,
        n_ics: int = 0,
        gpa=AbatementLevel.GPA97,
        fab_ci=EnergyLocation.TAIWAN,
    ) -> Carbon:
        """
        Get the total carbon emissions for a given logic process, area, and fabrication yield.

        Args:
            logic_process (LogicProcess): The logic process to calculate carbon emissions for.
            area (pint.Quantity): The area of the logic process.
            fab_yield (float, optional): The fabrication yield. Defaults to DEFAULT_FAB_YIELD.
            n_ics (int, optional): The number of ICs. Defaults to 0.
            gpa (AbatementLevel): Manufacturing gas abatement level. Defaults to AbatementLevel.GPA97.
            fab_ci (EnergyLocation): Carbon intensity of logic manufacturing. Defaults to EnergyLocation.TAIWAN.

        Returns:
            Carbon: The total carbon emissions.

        Raises:
            SystemExit: If the logic process is not found in any of the models.
        """
        assert area.check(mm2)
        """Query the model to get the carbon impact results"""
        if logic_process not in self.epa_model:
            log.error(
                f"Logic process {logic_process} not found in EPA model {self.epa_model}."
            )
            exit(-1)
        if logic_process not in self.gpa_model[gpa]:
            log.error(
                f"Logic process {logic_process} not found in GPA model {self.gpa_model}."
            )
            exit(-1)
        if logic_process not in self.materials_model:
            log.error(
                f"Logic process {logic_process} not found in materials model {self.materials_model}."
            )
            exit(-1)
        cpa = self.get_cpa(
            logic_process=logic_process, fab_yield=fab_yield, gpa=gpa, fab_ci=fab_ci
        )
        carbon = Carbon(area * cpa, SourceType.FABRICATION) + Carbon(
            n_ics * CARBON_PER_IC_PACKAGE, SourceType.PACKAGING
        )
        return carbon

    def get_carbon_energy(
        self, logic_process: LogicProcess, fab_ci=EnergyLocation.TAIWAN
    ) -> pint.Quantity:
        """
        Get the carbon emissions from energy consumption for a given logic process.

        Args:
            logic_process (LogicProcess): The logic process to calculate carbon emissions from energy consumption for.
            fab_ci (EnergyLocation): Carbon intensity of logic manufacturing. Defaults to EnergyLocation.TAIWAN.

        Returns:
            pint.Quantity: The carbon emissions from energy consumption.
        """
        carbon_energy = self.ci_model[fab_ci] * self.epa_model[logic_process]
        return carbon_energy

    def get_carbon_gas(
        self, logic_process: LogicProcess, gpa=AbatementLevel.GPA97
    ) -> pint.Quantity:
        """
        Get the carbon emissions from gas consumption for a given logic process.

        Args:
            logic_process (LogicProcess): The logic process to calculate carbon emissions from gas consumption for.
            gpa (AbatementLevel): Manufacturing gas abatement level. Defaults to AbatementLevel.GPA97.

        Returns:
            pint.Quantity: The carbon emissions from gas consumption.
        """
        carbon_gas = self.gpa_model[gpa][logic_process]
        return carbon_gas

    def get_carbon_materials(self, logic_process: LogicProcess) -> pint.Quantity:
        """
        Get the carbon emissions from materials consumption for a given logic process.

        Args:
            logic_process (LogicProcess): The logic process to calculate carbon emissions from materials consumption for.

        Returns:
            pint.Quantity: The carbon emissions from materials consumption.
        """
        carbon_materials = self.materials_model[logic_process]
        return carbon_materials
