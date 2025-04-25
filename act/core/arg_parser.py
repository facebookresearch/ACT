# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import argparse

from .common import *
from .bom import BOM
from .units import units


def get_parser():
    """
    Returns an ArgumentParser instance for the ACT carbon modeling tool.

    The parser includes arguments for output directory, materials, logic area,
    DRAM size, SSD size, HDD size, operating power, DRAM process, SSD process,
    HDD process, logic process, log level, number of ICs, number of capacitors,
    PCB area, and export file.
    """
    parser = argparse.ArgumentParser(description="ACT carbon modeling tool.")

    add_ci_args(parser)
    add_yield_args(parser)
    add_lifetime_args(parser)
    add_abatement_arg(parser)

    parser.add_argument(
        "-o",
        "--out-dir",
        type=str,
        default=None,
        help="Output directory for result files",
    )

    parser.add_argument(
        "-m",
        "--materials",
        type=str,
        default=None,
        help="Bill of materials list file to add to the total emissions cost.",
    )

    parser.add_argument(
        "--logic-area",
        type=str,
        default="0cm2",
        help="Total logic silicon area. Must have units of area (ex., 13cm2, 500mm2, etc.).",
    )

    parser.add_argument(
        "--dram-size",
        type=str,
        default="0GB",
        help="DRAM capacity. Must have units of storage (ex., 1.2GB, 543MB, etc.).",
    )

    parser.add_argument(
        "--ssd-size",
        type=str,
        default="0GB",
        help="SSD capacity. Must have units of storage (ex., 1.5GB, 43MB, etc.).",
    )

    parser.add_argument(
        "--hdd-size",
        type=str,
        default="0GB",
        help="HDD capacity. Must have units of storage (ex., 1.5GB, 75MB, etc.)",
    )

    parser.add_argument(
        "--op-power",
        default="0mW",
        type=str,
        help="Device operating power. Must have units of power (ex. 100mW, 10W etc.).",
    )

    parser.add_argument(
        "--dram-process",
        type=str,
        default=DRAMProcess.DDR4_10NM,
        help=f"DRAM fabrication process. Must be one of {[x.value for x in DRAMProcess]}",
    )

    parser.add_argument(
        "--ssd-process",
        type=str,
        default=SSDProcess.NAND_10NM,
        help=f"SSD fabrication process. Must be one of {[x.value for x in SSDProcess]}",
    )

    parser.add_argument(
        "--hdd-process",
        type=str,
        default=HDDProcess.BARRACUDA,
        help=f"HDD manufacturer. Must be one of {[x.value for x in HDDProcess]}",
    )

    parser.add_argument(
        "--logic-process",
        default=14,
        type=int,
        help="Technology node geometric in nm for logic. Must be an integer value corresponding to geometry.",
    )

    parser.add_argument(
        "-l",
        "--loglevel",
        type=str,
        default="info",
        help="Log level to report messages and telemetry.",
    )

    parser.add_argument(
        "--ics", type=int, default=0, help="Number of ICs that need to be packaged"
    )
    parser.add_argument(
        "--caps", type=int, default=0, help="Number of capacitors in the system"
    )
    parser.add_argument(
        "--pcb-area",
        type=str,
        default="0mm2",
        help=f"Printed circuit board area with units (ex., 10mm2, 152cm2)",
    )
    parser.add_argument(
        "--export-file", type=str, default=None, help="Output file for results from ACT"
    )

    return parser


def add_yield_args(parser):
    """
    Adds yield-related arguments to the parser.

    The added arguments include logic yield, DRAM yield, SSD yield, and HDD yield.
    """
    parser.add_argument(
        "--logic-yield",
        type=float,
        default=1.0,
        help="Chip yield rate for logic. Must be 0 < yield <= 1.0",
    )
    parser.add_argument(
        "--dram-yield",
        type=float,
        default=1.0,
        help="Yield rate for DRAM. Must be 0 < yield <= 1.0",
    )
    parser.add_argument(
        "--ssd-yield",
        type=float,
        default=1.0,
        help="Yield rate for SSD. Must be 0 < yield <= 1.0",
    )
    parser.add_argument(
        "--hdd-yield",
        type=float,
        default=1.0,
        help="Yield rate for HDD. Must be 0 < yield <= 1.0",
    )


def add_ci_args(parser):
    """
    Adds carbon intensity-related arguments to the parser.

    The added arguments include fab CI, cap CI, and op CI.
    """
    parser.add_argument(
        "--fab-ci",
        default=DEFAULT_FAB_LOCATION.value,
        type=str,
        help=f"Carbon intensity configuration for device fabrication. Either a location from {[x.value for x in EnergyLocation]} or an energy mix source from {[x.value for x in EnergySource]} must be specified. By default will use {DEFAULT_FAB_LOCATION}.",
    )

    parser.add_argument(
        "--cap-ci",
        default=DEFAULT_FAB_LOCATION.value,
        type=str,
        help=f"Carbon intensity configuration for capacitor fabrication. Either a location from {[x.value for x in EnergyLocation]} or an energy mix source from {[x.value for x in EnergySource]} must be specified. By default will use {DEFAULT_FAB_LOCATION}.",
    )

    parser.add_argument(
        "--op-ci",
        default=DEFAULT_OP_LOCATION,
        type=str,
        help=f"Carbon intensity configuration for device operation. Either a location from {[x.value for x in EnergyLocation]} or an energy mix source from {[x.value for x in EnergySource]} must be specified. By default will use {DEFAULT_OP_LOCATION}.",
    )


def add_lifetime_args(parser):
    """
    Adds lifetime-related arguments to the parser.

    The added arguments include duty cycle and lifetime.
    """
    parser.add_argument(
        "--duty-cycle",
        type=float,
        default=1.0,
        help="Device duty cycle as a fraction from 0 to 1 which calculates the OPERATION energy cost.",
    )

    parser.add_argument(
        "--lifetime",
        type=str,
        default="2years",
        help="The estimated device lifetime before it will be replaced. (ex., 2years, 15days).",
    )


def add_abatement_arg(parser):
    """
    Adds abatement-related argument to the parser.

    The added argument includes gpa (gasses abatement percentage level).
    """
    parser.add_argument(
        "--gpa",
        type=int,
        default=97,
        help=f"Gasses abatement percentage level for gasses per area parameter. Options: {[x.value for x in AbatementLevel]}",
    )


def get_clean_args(args):
    """
    Returns a tuple of model arguments and query arguments based on the input arguments.

    The model arguments include out_dir, and the query arguments include bom, op_ci,
    op_power, duty_cycle, hw_lifetime, and export_file.
    """
    op_ci = get_src_or_loc(args.op_ci)
    fab_ci = get_src_or_loc(args.op_ci)

    model_args = dict(out_dir=args.out_dir)

    bom = BOM(
        silicon=dict(
            logic=dict(
                area=args.logic_area,
                fab_yield=float(args.logic_yield),
                process=LogicProcess(f"{args.logic_process}nm"),
                fab_ci=fab_ci,
                gpa=AbatementLevel(args.gpa),
            ),
            dram=dict(
                model="dram",
                capacity=args.dram_size,
                fab_yield=float(args.dram_yield),
                process=DRAMProcess(args.dram_process),
            ),
            ssd=dict(
                model="flash",
                capacity=args.ssd_size,
                fab_yield=float(args.ssd_yield),
                process=SSDProcess(args.ssd_process),
            ),
            hdd=dict(
                model="hdd",
                capacity=args.hdd_size,
                fab_yield=float(args.hdd_yield),
                process=HDDProcess(args.hdd_process),
            ),
        )
    )

    query_args = dict(
        bom=bom,
        op_ci=op_ci,
        op_power=units(args.op_power),
        duty_cycle=float(args.duty_cycle),
        hw_lifetime=units(args.lifetime),
        export_file=args.export_file,
    )

    return model_args, query_args
