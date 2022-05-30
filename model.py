
# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import sys

from dram_model  import Fab_DRAM
from ssd_model   import Fab_SSD
from logic_model import Fab_Logic

def main():
    Fab_DRAM(config="ddr4_10nm")
    Fab_SSD(config="nand_10nm")

    Fab_Logic(gpa="95", carbon_intensity = "src_coal", debug=True,
              process_node=10)

#    Fab_Logic(gpa="97", carbon_intensity = "loc_taiwan", debug=True,
#              process_node=14)


if __name__=="__main__":
    main()
