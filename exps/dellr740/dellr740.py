
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

##############################
# Original Dell 740 LCA
##############################
#https://corporate.delltechnologies.com/content/dam/digitalassets/active/en/unauth/data-sheets/products/servers/lca_poweredge_r740.pdf

##############################
# Main Dell R740 integrated circuits
##############################
dellr740_large_ssd = 3840 # GB (3.84 TB x 8 SSD's)
dellr740_ssd       = 400 # GB (400GB x 1 SSD)
dellr740_ssd_dram  = 68 # GB (64 + 4GB ECC)
dellr740_dram      = 36 # GB (32 + 4 ECC GB x 12)
ic_yield           = 0.875

cpu_area = 6.98 #cm^2

##############################
# Estimated process technology node to mimic fairphone LCA process node
##############################
CPU_Logic = Fab_Logic(gpa  = "95",
                      carbon_intensity = "src_coal",
                      process_node = 28,
                      fab_yield=ic_yield)

SSD_main           = Fab_SSD(config  = "nand_30nm", fab_yield = ic_yield)
SSD_secondary      = Fab_SSD(config  = "nand_30nm", fab_yield = ic_yield)
DRAM_SSD_main      = Fab_DRAM(config = "ddr3_50nm", fab_yield = ic_yield)
DRAM_SSD_secondary = Fab_DRAM(config = "ddr3_50nm", fab_yield = ic_yield)
DRAM               = Fab_DRAM(config = "ddr3_50nm", fab_yield = ic_yield)

##############################
# Computing carbon footprint of IC's
##############################
CPU_Logic.set_area(cpu_area)
DRAM.set_capacity(dellr740_dram)

DRAM_SSD_main.set_capacity(dellr740_ssd_dram)
SSD_main.set_capacity(dellr740_large_ssd)

DRAM_SSD_secondary.set_capacity(dellr740_ssd_dram)
SSD_secondary.set_capacity(dellr740_ssd)

##################################
# Computing the packaging footprint
##################################
# number of packages
ssd_main_nr         = 12 + 1
ssd_secondary_nr    = 12 + 1
dram_nr             = 18 + 1
cpu_nr              = 2
packaging_intensity = 150 # gram CO2

SSD_main_packaging      = packaging_intensity * ssd_main_nr
SSD_secondary_packaging = packaging_intensity * ssd_secondary_nr
DRAM_packging           = packaging_intensity * dram_nr
CPU_packaging           = packaging_intensity * cpu_nr

total_packaging = SSD_main_packaging +  \
                  SSD_secondary_packaging + \
                  DRAM_packging + \
                  CPU_packaging
total_packaging = total_packaging / 1000.

##################################
# Compute end-to-end carbon footprints
##################################
SSD_main_count = 8 # There are 8x3.84TB SSD's
SSD_main_co2 = (SSD_main.get_carbon() + \
                DRAM_SSD_main.get_carbon() + \
                SSD_main_packaging) / 1000.
SSD_main_co2 = SSD_main_co2 * SSD_main_count

SSD_secondary_count = 1 # There are 1x400GB SSD's
SSD_secondary_co2 = (SSD_secondary.get_carbon() + \
                     DRAM_SSD_secondary.get_carbon() +  \
                     SSD_secondary_packaging) / 1000.
SSD_secondary_co2 = SSD_secondary_co2 * SSD_secondary_count

DRAM_count = 12 # There are 12 x (32GB+4GB ECC DRAM modules)
DRAM_co2 = (DRAM.get_carbon() + DRAM_packging) / 1000. * DRAM_count

CPU_count = 2
CPU_co2   = (CPU_Logic.get_carbon() + CPU_packaging) * CPU_count / 1000.

if debug:
    print("ACT SSD main", SSD_main_co2, "kg CO2")
    print("ACT SSD secondary", SSD_secondary_co2, "kg CO2")
    print("ACT DRAM", DRAM_co2, "kg CO2")
    print("ACT CPU", CPU_co2, "kg CO2")
    print("ACT Packaging", total_packaging, "kg CO2")

print("--------------------------------")
print("ACT SSD main", SSD_main_co2, "kg CO2 vs. LCA 3373 kg CO2")
print("ACT SSD secondary", SSD_secondary_co2, "kg CO2 vs. LCA 64.1 kg CO2")
print("ACT DRAM", DRAM_co2, "kg CO2 vs. LCA 533 kg CO2")
print("ACT CPU", CPU_co2, "kg CO2 vs. LCA 47 kg CO2")
