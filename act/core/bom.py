# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass

from .capacitor_model import CapacitorType
from .units import *
import os
from enum import Enum
from typing import Union

import pint
import yaml

from .carbon import SourceType

from .common import (
    AbatementLevel,
    ComponentCategory,
    DEFAULT_FAB_YIELD,
    DRAMProcess,
    EnergyLocation,
    get_src_or_loc,
    HDDProcess,
    LogicProcess,
    ModelType,
    SSDProcess,
)
from .logger import log

SILICON = "silicon"
CATEGORY = "category"
MATERIALS = "materials"
PASSIVES = "passives"
IMPORTS = "imports"


@dataclass
class BOM:
    name: str = "Default Materials List Name"
    owner: str = ""
    description: str = ""
    materials: dict = None  # frame/enclosure device materials
    passives: dict = None  # passive component devices
    silicon: dict = None  # silicon devices
    imports: dict = None  # any files to import (not recursive)
    file: str = None  # original file for this BOM
    material_type: Enum = None  # the material types

    def __post_init__(self):
        if self.passives is None:
            self.passives = dict()
        if self.materials is None:
            self.materials = dict()
        if self.silicon is None:
            self.silicon = dict()

        # import data from additional files if specified first
        if self.imports is not None:
            for iname, filepath in self.imports.items():
                path = os.path.dirname(self.file) + "/" + filepath
                with open(path) as handle:
                    file_data = yaml.load(handle, Loader=yaml.FullLoader)
                if MATERIALS in file_data:
                    for name, data in file_data[MATERIALS].items():
                        self.materials[f"{iname}.{name}"] = data
                if SILICON in file_data:
                    for name, data in file_data[SILICON].items():
                        self.silicon[f"{iname}.{name}"] = data
                if PASSIVES in file_data:
                    for name, data in file_data[PASSIVES].items():
                        self.passives[f"{iname}.{name}"] = data
                if IMPORTS in file_data:
                    log.warn(
                        f"File importing currently only works for a single level and is not recursive. Recursive import {file_data[IMPORTS]} in {path} will be ignored."
                    )

        # convert the dictionary to unit'ed structure and specifications
        passives = dict()
        if self.passives is not None:
            for cname, cdata in self.passives.items():
                cat = ComponentCategory(cdata[CATEGORY])
                if cat is ComponentCategory.CAPACITOR:
                    passives[cname] = CapacitorSpec(**cdata)
                elif cat is ComponentCategory.RESISTOR:
                    passives[cname] = ResistorSpec(**cdata)
                elif cat is ComponentCategory.SIGNAL_BEAD:
                    passives[cname] = BaseSpec(**cdata)
                else:
                    raise NotImplementedError(
                        f"Materials specification category {cat} for materials list item {cname} not defined."
                    )
        self.passives = passives

        # convert the frame materials
        if self.materials is not None:
            self.materials = {
                mname: MaterialSpec(**mdata, material_type=self.material_type)
                for mname, mdata in self.materials.items()
            }
        else:
            self.materials = dict()

        # convert the silicon annotation data structure
        silicon = dict()
        if self.silicon is not None:
            for dname, silicon_data in self.silicon.items():
                annotation = SiliconAnnotation(**silicon_data)
                silicon[dname] = annotation
        self.silicon = silicon


@dataclass
class SiliconAnnotation:
    model: ModelType = ModelType.LOGIC  # assume logic model by default
    area: str = "0 mm2"
    capacity: str = "0 GB"
    n_ics: int = 0
    process: Union[LogicProcess, DRAMProcess, SSDProcess, HDDProcess] = None
    carbon: str = None  # carbon amount if using manual type
    ctype: str = SourceType.FABRICATION  # carbon type if using manual model type
    fab_yield: float = DEFAULT_FAB_YIELD
    fab_ci: str = None
    gpa: AbatementLevel = None

    def __post_init__(self):
        self.area = units(self.area)
        self.model = ModelType(self.model)
        self.capacity = units(self.capacity)
        self.carbon = units(self.carbon) if self.carbon is not None else None
        self.ctype = SourceType(self.ctype)
        self.gpa = (
            AbatementLevel(self.gpa) if self.gpa is not None else AbatementLevel.GPA97
        )
        self.fab_ci = (
            get_src_or_loc(self.fab_ci)
            if self.fab_ci is not None
            else EnergyLocation.TAIWAN
        )

        if self.model is ModelType.LOGIC:
            self.process = (
                LogicProcess(self.process)
                if self.process is not None
                else LogicProcess.NA
            )
        elif self.model is ModelType.DRAM:
            self.process = (
                DRAMProcess(self.process)
                if self.process is not None
                else DRAMProcess.NA
            )
        elif self.model is ModelType.FLASH:
            self.process = (
                SSDProcess(self.process) if self.process is not None else SSDProcess.NA
            )
        elif self.model is ModelType.HDD:
            self.process = (
                HDDProcess(self.process) if self.process is not None else HDDProcess.NA
            )
        else:  # by default convert with logic process for now
            self.process = (
                LogicProcess(self.process)
                if self.process is not None
                else LogicProcess.NA
            )


@dataclass
class BaseSpec:  # common materials specifications
    category: str
    quantity: int = 0
    weight: pint.Quantity = "0 g"
    area: pint.Quantity = "0 mm2"
    capacity: pint.Quantity = "0 kWh"
    fab_ci: str = None
    layers: int = None

    def __post_init__(self):
        self.weight = units(self.weight)
        self.category = ComponentCategory(self.category)
        self.area = units(self.area)
        self.capacity = units(self.capacity)
        self.fab_ci = (
            get_src_or_loc(self.fab_ci)
            if self.fab_ci is not None
            else EnergyLocation.JAPAN
        )


@dataclass
class CapacitorSpec(BaseSpec):
    type: str = CapacitorType.GENERIC.value

    def __post_init__(self):
        super().__post_init__()
        self.type = CapacitorType(self.type)


@dataclass
class ResistorSpec(BaseSpec):
    type: str = ""


@dataclass
class MaterialSpec(BaseSpec):
    type: str = ""  # the material type
    material_type: Enum = None

    def __post_init__(self):
        super().__post_init__()
        self.type = (
            self.material_type(self.type) if self.type else self.material_type.NA
        )


def load_bom(materials_file: str, material_type: Enum):
    """Load the materials file and return a BOM data structure"""

    with open(materials_file) as handle:
        materials_data = yaml.load(handle, Loader=yaml.FullLoader)
    materials = BOM(**materials_data, file=materials_file, material_type=material_type)
    return materials
