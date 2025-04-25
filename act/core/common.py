# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from enum import Enum

from .units import *

"""
Root directory of the project.
"""
ACT_ROOT = os.path.dirname(__file__) + "/.."


def get_src_or_loc(arg):
    """
    Attempts to create an EnergySource or EnergyLocation instance from the given argument.

    Args:
        arg: The argument to create an EnergySource or EnergyLocation instance from.

    Returns:
        An instance of EnergySource or EnergyLocation.
    """
    try:
        ci = EnergySource(arg)
    except ValueError:
        ci = EnergyLocation(arg)
    return ci


class LogicProcess(Enum):
    """
    Enum representing different logic processes.
    """

    N65 = "65nm"
    N45 = "45nm"
    N40 = "40nm"
    N28 = "28nm"
    N20 = "20nm"
    N14 = "14nm"
    N10 = "10nm"
    N8 = "8nm"
    N7 = "7nm"
    N7_EUV = "7nm_EUV"
    N5 = "5nm"
    N3 = "3nm"
    N2 = "2nm"
    N2_BSP = "2nm_BSP"
    A14 = "14a"
    A10 = "10a"
    NA = "na"


class DRAMProcess(Enum):
    """
    Enum representing different DRAM processes.
    """

    DDR3_50NM = "ddr3_50nm"
    DDR3_40NM = "ddr3_40nm"
    DDR3_30NM = "ddr3_30nm"
    LPDDR3_30NM = "lpddr3_30nm"
    LPDDR3_20NM = "lpddr3_20nm"
    LPDDR2_20NM = "lpddr2_20nm"
    LPDDR4 = "lpddr4"
    DDR4_10NM = "ddr4_10nm"
    NA = "na"


class SSDProcess(Enum):
    """
    Enum representing different SSD processes.
    """

    NAND_30NM = "nand_30nm"
    NAND_20NM = "nand_20nm"
    NAND_10NM = "nand_10nm"
    NAND_TLC_1Z = "nand_tlc_1z"
    NAND_TLC_V3 = "nand_tlc_v3"
    SEAGATE_3530 = "seagate_nytro_3530"
    SEAGATE_1551 = "seagate_nytro_1551"
    SEAGATE_3331 = "seagate_nytro_3331"
    WD_2016 = "western_digital_2016"
    WD_2017 = "western_digital_2017"
    WD_2018 = "western_digital_2018"
    WD_2019 = "western_digital_2019"
    NA = "na"


class HDDProcess(Enum):
    """
    Enum representing different HDD processes.
    """

    BARRACUDA = "BarraCuda"
    BARRACUDA2 = "BarraCuda2"
    BARRACUDA_PRO = "BarraCuda Pro"
    FIRECUDA = "FireCuda"
    FIRECUDA2 = "FireCuda2"
    IRONWOLF = "IronWolf"
    IRONWOLFPRO = "IronWolfPro"
    SKYHAWK3TB = "SkyWalk3TB"
    SKYHAWK_SURV = "Skyhawk Surveillance"
    SKYHAWK6TB = "Skyhawk-6TB"
    VIDEO_HDD = "VideoHDD"
    VIDEO_PHDD = "VideoPipelineHDD"
    EXOS2X14 = "Exos2x14"
    EXOSX12 = "Exosx12"
    EXOSX16 = "Exosx16"
    EXOS15 = "Exos15e900"
    EXOS10 = "Exos10e2400"
    EXOS500 = "Exos5e8"
    EXOS700 = "Exos7e8"
    NA = "na"


class EnergyLocation(Enum):
    """
    Enum representing different energy locations.
    """

    WORLD = "world"
    INDIA = "india"
    AUSTRALIA = "australia"
    JAPAN = "japan"
    KOREA = "korea"
    TAIWAN = "taiwan"
    SINGAPORE = "singapore"
    USA = "usa"
    EUROPE = "europe"
    BRAZIL = "brazil"
    ICELAND = "iceland"


class EnergySource(Enum):
    """
    Enum representing different energy sources.
    """

    COAL = "coal"
    GAS = "gas"
    BIOMASS = "biomass"
    SOLAR = "solar"
    GEOTHERMAL = "geothermal"
    HYDROPOWER = "hydropower"
    NUCLEAR = "nuclear"
    WIND = "wind"


"""
Default fabrication source.
"""
DEFAULT_FAB_SOURCE = EnergySource.COAL

"""
Default operation location.
"""
DEFAULT_OP_LOCATION = EnergyLocation.USA

"""
Default fabrication location.
"""
DEFAULT_FAB_LOCATION = EnergyLocation.TAIWAN

"""
Default fabrication yield.
"""
DEFAULT_FAB_YIELD = 0.875


class AbatementLevel(Enum):
    """
    Enum representing different abatement levels.
    """

    GPA95 = 95
    GPA97 = 97
    GPA99 = 99


class ComponentCategory(Enum):
    """
    Enum representing different component categories.
    """

    CAPACITOR = "capacitor"
    RESISTOR = "resistor"
    DIODE = "diode"
    FRAME = "frame"
    ENCLOSURE = "enclosure"
    SILICON = "silicon"
    PCB = "pcb"
    BATTERY = "battery"
    SIGNAL_BEAD = "signal bead"
    OTHER = "other"


class ModelType(Enum):
    """
    Enum representing different model types.
    """

    LOGIC = "logic"
    DRAM = "dram"
    FLASH = "flash"
    HDD = "hdd"
    MANUAL = "manual"


"""
Carbon per IC package in grams.
"""
CARBON_PER_IC_PACKAGE = 150 * g
