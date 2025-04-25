# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from enum import auto, Enum

import pint

from .units import g


# Track the type of each emissions component
class SourceType(Enum):
    """
    Enum representing the type of each emissions component.
    """

    PACKAGING = auto()  # Cost from IC packaging process
    MATERIALS = auto()  # Cost of IC materials procurement
    OPERATION = auto()  # Cost of operating device
    FABRICATION = auto()  # Cost of powering and using the fab
    PASSIVES = auto()  # Cost of passives like capacitors, resistors, and diodes
    PCB = auto()  # PCB manufacturing cost
    CONNECTOR = auto()  # Connector passives cost
    ENCLOSURE = auto()  # Enclosure cost like case, plastic frames, etc.
    OTHER = auto()  # Miscellaneous source type


class Carbon:
    """
    A wrapper class around carbon results.

    Attributes:
        carbon_by_type (dict): A dictionary mapping SourceType to amounts of carbon.
    """

    def __init__(
        self,
        amount: pint.Quantity = None,
        ctype: SourceType = None,
        result_dict: dict[SourceType, pint.Quantity] = None,
    ) -> None:
        """
        Initializes a new instance of the Carbon class.

        Args:
            amount (pint.Quantity, optional): Amount of carbon with units of weight. Defaults to None.
            ctype (SourceType, optional): The emissions source type. If None is specified, will default to SourceType.OTHER
            result_dict (dict[SourceType, pint.Quantity], optional): A dictionary mapping SourceType to amounts of carbon. Used to initialize the object instead of the amount and ctype if provided.
        """
        # Initialize from dict if specified
        if result_dict is not None:
            self.carbon_by_type = result_dict
        else:
            assert amount.check(
                g
            ), f"Carbon amount must be in units of weight. Got {amount}"
            if ctype is not None and ctype not in SourceType:
                _ctype = SourceType.OTHER
            else:
                _ctype = ctype
            self.carbon_by_type = {_ctype: amount}

    def _get_other_keys(self, other: "Carbon") -> list[SourceType]:
        """
        Get the keys from another Carbon instance.

        Args:
            other (Carbon): The other Carbon instance.

        Returns:
            list[SourceType]: The keys from the other Carbon instance.
        """
        if other == 0:  # Handle zero that comes in through sums
            other_keys = []
        else:
            other_keys = list(other.carbon_by_type.keys())
        return other_keys

    def __add__(self, other: "Carbon") -> "Carbon":
        """
        Add another Carbon instance to this one.

        Args:
            other (Carbon): The other Carbon instance.

        Returns:
            Carbon: A new Carbon instance representing the sum of this one and the other.
        """
        # Add another carbon result
        new_result = {}
        keys = self._get_other_keys(other) + list(self.carbon_by_type.keys())
        for k in keys:
            x = self.carbon_by_type.get(k, 0 * g)
            y = other.carbon_by_type.get(k, 0 * g) if other != 0 else 0
            new_result[k] = x + y
        return Carbon(result_dict=new_result)

    def __sub__(self, other: "Carbon") -> "Carbon":
        """
        Subtract another Carbon instance from this one.

        Args:
            other (Carbon): The other Carbon instance.

        Returns:
            Carbon: A new Carbon instance representing the difference between this one and the other.
        """
        # Subtract another carbon result
        new_result = {}
        keys = self._get_other_keys(other) + list(self.carbon_by_type.keys())
        for k in keys:
            x = self.carbon_by_type.get(k, 0 * g)
            y = other.carbon_by_type.get(k, 0 * g) if other != 0 else 0
            new_result[k] = x - y
        return Carbon(result_dict=new_result)

    def __radd__(self, other: int) -> "Carbon":
        """
        Add this Carbon instance to an integer (for sum) or other Carbon instances.

        Args:
            other (int): The integer.

        Returns:
            Carbon: This Carbon instance if the integer is 0, otherwise the result of adding this Carbon instance to the integer.
        """
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def partial(self, ctype: SourceType) -> pint.Quantity:
        """
        Get the partial amount of carbon for a given SourceType.

        Args:
            ctype (SourceType): The SourceType.

        Returns:
            pint.Quantity: The partial amount of carbon.
        """
        return self.carbon_by_type.get(ctype, 0 * g)

    def total(self) -> pint.Quantity:
        """
        Get the total amount of carbon.

        Returns:
            pint.Quantity: The total amount of carbon.
        """
        # Return summed total over all carbon contribution components
        return sum([v for _, v in self.carbon_by_type.items()])

    def types(self) -> list[SourceType]:
        """
        Get the SourceTypes present in this Carbon instance.

        Returns:
            list[SourceType]: The SourceTypes.
        """
        return list(self.carbon_by_type.keys())
