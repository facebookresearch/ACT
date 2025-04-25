# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from .utils import DEFAULT_LOCATION_CONFIG, DEFAULT_SOURCE_CONFIG, load_ci_model
from .units import *
from .carbon import Carbon, SourceType
from .logger import log


class OpModel:
    def __init__(
        self,
        loc_ci_config=DEFAULT_LOCATION_CONFIG,
        src_ci_config=DEFAULT_SOURCE_CONFIG,
    ) -> None:
        """Load the operation models

        Args:
            loc_ci_config(str): The location carbon intensity configuration model file
            src_ci_config(str): The energy source type carbon intensity confguration model file

        """
        self.ci_model = load_ci_model(
            loc_ci_config=loc_ci_config, src_ci_config=src_ci_config
        )

    def get_carbon(
        self,
        lifetime: units,
        duty_cycle: float,
        op_power: units,
        op_ci: str,
    ) -> Carbon:
        """Get the estimated carbon operation costs.

        Args:
            lifetime (units): The estimated device lifetime.
            duty_cycle (float): The estimated device active duty cycle.
            op_power (units): The average operating power of the device.
            op_ci (str): The carbon intensity of the energy grid for operation.
        Returns:
            Carbon: The total carbon emissions from operation.
        Raises:
            SystemExit: If the lifetime does not have units of time.
        """
        if not lifetime.check(s):
            log.error(
                f"Operating lifetime of device must have units of time. Got {lifetime}"
            )
            exit(-1)

        op_ci = self.ci_model[op_ci]
        op_time = lifetime * duty_cycle
        carbon = op_ci * op_power * op_time

        return Carbon(carbon, SourceType.OPERATION)
