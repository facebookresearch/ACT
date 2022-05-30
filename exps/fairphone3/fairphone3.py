
# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import sys

from dram_model import Fab_DRAM
from hdd_model  import Fab_HDD
from ssd_model  import Fab_SSD
from logic_model  import Fab_Logic

debug = False

# Main Fairphone integrated circuits
fairphone3_ICs = ["IC analog switch",
        "LED Flash",
        "LED Flash",
        "CMOS image sensor",
        "Light sensor",
        "Light sensor",
        "LED Full Color",
        "Image sensor",
        "I.C WLAN",
        "I.C WLAN",
        "Audio power amplifier",
        "IC analog switch",
        "IC power amplifier",
        "IC PMU",
        "IC PMU",
        "IC PMU",
        "Sensor",
        "NFC Microcontroller",
        "IC transceiver",
        "IC audio power",
       ]

# Main Fairphone integrated circuits' areas in mm^2
fairphone3_IC_areas = [0.85,
         1.2,
         1.2,
         35,
         0.89,
         0.08,
         0.25,
         18,
         11.6,
         1.44,
         12.96,
         1.61,
         6.3,
         26.88,
         0.77,
         11.36,
         7,
         8.69,
         11,
         9.6]

fairphone_cpu_area = 46.4 #mm^2
fairphone_ram      = 4 # GB
fairphone_storage  = 64 # GB
ic_yield           = 0.875

##################################
# Estimated process technology node to mimic fairphone LCA process node
# This initializes ACT with an older technology node.
##################################

# IC Logic node
IC_Logic = Fab_Logic(gpa = "95",
                     carbon_intensity = "src_coal",
                     process_node = 28,
                     fab_yield=ic_yield)

# CPU Application processor node
CPU_Logic = Fab_Logic(gpa  = "95",
                      carbon_intensity = "src_coal",
                      process_node = 28,
                      fab_yield=ic_yield)

# DRAM Logic node
DRAM  = Fab_DRAM(config = "ddr3_50nm", fab_yield=ic_yield)

# SSD Logic node
SSD   = Fab_SSD(config  = "nand_30nm", fab_yield=ic_yield)


##################################
# Computing the IC footprint
##################################
IC_Logic.set_area(sum(fairphone3_IC_areas)/100.)
CPU_Logic.set_area(fairphone_cpu_area/100.)
DRAM.set_capacity(fairphone_ram)
SSD.set_capacity(fairphone_storage)

##################################
# Computing the packaging footprint
##################################
#Number of packages
nr = len(fairphone3_ICs) + 1 + 1 + 1 # Fairphone ICs + CPU + DRAM + SSD
packaging_intensity = 150 # gram CO2

PackagingFootprint = nr * packaging_intensity

if debug:
    print("ACT IC", IC_Logic.get_carbon(), "g CO2")
    print("ACT CPU", CPU_Logic.get_carbon(), "g CO2")
    print("ACT DRAM", DRAM.get_carbon(), "g CO2")
    print("ACT SSD", SSD.get_carbon(), "g CO2")
    print("ACT Packaging", PackagingFootprint, "g CO2")

print("--------------------------------")
ram_flash = (DRAM.get_carbon() + SSD.get_carbon() + packaging_intensity * 2) / 1000.
fairphone_ram_flash = 11
print("ACT RAM + Flash", ram_flash, "kg CO2 vs. LCA", fairphone_ram_flash, "kg CO2")

cpu = (CPU_Logic.get_carbon() + packaging_intensity) / 1000.
fairphone_cpu = 1.07
print("ACT CPU", cpu, "kg CO2 vs. LCA", fairphone_cpu, "kg CO2")

ics = (IC_Logic.get_carbon() + packaging_intensity * len(fairphone3_ICs)) / 1000.
fairphone_ics = 5.3
print("ACT ICs", ics, "kg CO2 vs. LCA", fairphone_ics, "kg CO2")

