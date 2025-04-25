# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from enum import Enum

import yaml

from .carbon import Carbon, SourceType
from .common import ACT_ROOT
from .units import g, units

DEFAULT_MATERIALS_CONFIG = f"{ACT_ROOT}/models/materials/materials.yaml"


class MaterialsModel:
    """
    A model for estimating carbon emissions from materials.

    Attributes:
        model (dict): A dictionary mapping material types to their corresponding carbon costs.
        MaterialType (Enum): An enumeration of material types, dynamically generated from the model file.
    """

    def __init__(self, model_file: str = DEFAULT_MATERIALS_CONFIG) -> None:
        """
        Initializes a new instance of the MaterialsModel class.

        Loads the materials data from a YAML file and constructs the model.

        Args:
            model_file (str, optional): The path to the materials data file. Defaults to DEFAULT_MATERIALS_CONFIG.
        """
        with open(model_file) as handle:
            model_data = yaml.load(handle, Loader=yaml.FullLoader)
        materials_data = model_data["materials"]

        # Dynamically generate the materials enum
        self.MaterialType = Enum(
            "MaterialType",
            {**{x.upper(): x for x in materials_data.keys()}, "NA": "na"},
        )

        self.model = {self.MaterialType(k): units(v) for k, v in materials_data.items()}
        for k, v in self.model.items():
            assert v.check(
                g / g
            ), f"Materials cost must be dimensionless. Got {v} for material {k}."

    def get_carbon(self, mat, weight: units) -> Carbon:
        """
        Get the estimated carbon emissions from a given material and weight.

        Args:
            mat (MaterialType): The type of material where MaterialType enum is dynamically loaded from the model file.
            weight (pint.Quantity): The weight of the material.

        Returns:
            Carbon: The total carbon emissions from the material.

        Raises:
            AssertionError: If the weight is not in units of weight.
        """
        assert weight.check(g), f"Weight should be in units of weight but got {weight}"
        c_per_kg = self.model[self.MaterialType(mat)]
        c = c_per_kg * weight
        return Carbon(c, SourceType.ENCLOSURE)
