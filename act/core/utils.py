# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import yaml
from .units import *

import math
from enum import auto, Enum

from .common import ACT_ROOT, EnergyLocation, EnergySource

from .logger import log

DEFAULT_LOCATION_CONFIG = f"{ACT_ROOT}/models/carbon_intensity/location.yaml"
DEFAULT_SOURCE_CONFIG = f"{ACT_ROOT}/models/carbon_intensity/source.yaml"


def load_ci_model(
    loc_ci_config=DEFAULT_LOCATION_CONFIG, src_ci_config=DEFAULT_SOURCE_CONFIG
):
    """
    Load the carbon intensity model for the fab. Shared by the logic and OPERATION models.

    Args:
        loc_ci_config (str): The location configuration file path. Defaults to DEFAULT_LOCATION_CONFIG.
        src_ci_config (str): The source configuration file path. Defaults to DEFAULT_SOURCE_CONFIG.

    Returns:
        dict: A dictionary mapping EnergyLocation or EnergySource to carbon intensity.
    """
    ci_model = {}
    with open(loc_ci_config) as f:
        loc_model = yaml.load(f, Loader=yaml.FullLoader)
        loc_model = {EnergyLocation(k): units(v) for k, v in loc_model.items()}
        ci_model.update(loc_model)

    with open(src_ci_config) as f:
        src_model = yaml.load(f, Loader=yaml.FullLoader)
        src_model = {EnergySource(k): units(v) for k, v in src_model.items()}
        ci_model.update(src_model)

    return ci_model


DEFAULT_DEFECT_DENSITY = 0.15 / cm2


# Yield utility arg check function
def check_args(area, density):
    """
    Check if the provided area and density have the correct units.

    Args:
        area: The area to check.
        density: The density to check.

    Raises:
        SystemExit: If the area or density have incorrect units.
    """
    if not area.check(mm2):
        log.error(f"Yield area must have area units. Got {area}")
        exit(-1)
    if not density.check(1 / mm2):
        log.error(f"Yield defect density must have units of 1 / area. Got {density}")
        exit(-1)


# Fabrication yield models transcribed from https://www.eesemi.com/test-yield-models.htm
def poisson_model(area, density):
    """
    Calculate the die yield using the Poisson model.

    Args:
        area: The area of the die.
        density: The defect density.

    Returns:
        float: The die yield.
    """
    check_args(area, density)
    die_yield = math.e(-area * density)
    return die_yield


class Distribution(Enum):
    """
    Enum representing different distribution types.
    """

    TRIANGLE = auto()
    RECT = auto()


def murphy_model(area, density, dist=Distribution.TRIANGLE):
    """
    Calculate the die yield using the Murphy model.

    Args:
        area: The area of the die.
        density: The defect density.
        dist (Distribution): The distribution type. Defaults to Distribution.TRIANGLE.

    Returns:
        float: The die yield.
    """
    check_args(area, density)
    _dist = Distribution(dist)
    if _dist == Distribution.TRIANGLE:
        die_yield = (1 - math.e(-area * density) / (area * density)) ** 2
    else:
        die_yield = (1 - math.e(-2 * area * density)) / (2 * area * density)
    return die_yield


def exponential_model(area, density):
    """
    Calculate the die yield using the exponential model.

    Args:
        area: The area of the die.
        density: The defect density.

    Returns:
        float: The die yield.
    """
    check_args(area, density)
    die_yield = 1 / (1 + area * density)
    return die_yield
