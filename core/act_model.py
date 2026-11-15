# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import datetime
import os
import pathlib
import tempfile

import pint
from act.core.act_result import ACTResult
from act.core.carbon import Carbon, SourceType
from act.core.common import DEFAULT_OP_YEAR, ModelType
from act.core.device_data import DeviceData
from act.core.gui.act_dashboard import ACTDashboard
from act.core.metrics.cost_analyzer import CostAnalyzer
from act.core.metrics.metric_analyzer import MetricAnalyzer
from act.core.models.ap_model import APModel, DEFAULT_AP_CONFIG
from act.core.models.battery_model import BatteryModel, DEFAULT_BATTERY_CONFIG
from act.core.models.capacitor_model import CapacitorModel, DEFAULT_CP_CONFIG
from act.core.models.ci_model import CIModel
from act.core.models.dram_model import DEFAULT_DRAM_CONFIG, DRAMModel
from act.core.models.hdd_model import DEFAULT_HDD_CONFIG, HDDModel
from act.core.models.imec_logic_model import IMECLogicModel
from act.core.models.logic_model import LogicModel
from act.core.models.manual_model import ManualModel
from act.core.models.materials_model import DEFAULT_MATERIALS_CONFIG, MaterialsModel
from act.core.models.op_model import OpModel
from act.core.models.pcb_model import PCBModel
from act.core.models.ssd_model import SSDModel
from act.core.scaling.apply_ci_scaling import apply_ci_scaling
from act.core.scaling.scaling_config import ScalingConfig
from act.core.scaling.tech_scaling_manager import TechScalingManager
from act.core.utils.load_yaml_with_macros import load_yaml_with_macros
from act.core.utils.logger import log
from act.core.utils.units import kg, year
from act.core.utils.utils import (
    resolve_duty_cycle,
    resolve_life_cycle,
    resolve_op_ci,
    resolve_op_power,
    resolve_op_year,
)

SYMLINK_PATH = "latest_act_out"
VIRTUAL_POWER_DEVICE = "__SYSTEM_POWER__"


class ACTModel:
    def __init__(
        self,
        out_dir: str = None,
        weight_unit=kg,
        ap_config=DEFAULT_AP_CONFIG,
        cap_config=DEFAULT_CP_CONFIG,
        dram_config=DEFAULT_DRAM_CONFIG,
        hdd_config=DEFAULT_HDD_CONFIG,
        materials_config=DEFAULT_MATERIALS_CONFIG,
        battery_config=DEFAULT_BATTERY_CONFIG,
        test=False,
        cl_macros=None,
        scaling_file=None,
        scaling_config=None,
        use_legacy=False,
    ):
        """Initialize the ACT Model object.

        Args:
            out_dir (str): Output directory for results.
            weight_unit (pint.Quantity): The unit of weight to normalize results to for reporting.
            ap_config (str): AP model configuration file path.
            cap_config (str): Capacitor model configuration file path.
            dram_config (str): DRAM model configuration file path.
            hdd_config (str): HDD model configuration file path.
            materials_config (str): Material model configuration file path.
            test (bool): If True, skip creating symlink for test runs.
            cl_macros (dict): Command line macros for YAML loading.
            scaling_file (str): Path to technology scaling configuration file.
            scaling_config (ScalingConfig): Pre-loaded scaling configuration object.
            use_legacy (bool): If True, use legacy carbon intensity models.
        """

        self.cl_macros = {} if cl_macros is None else cl_macros
        self.weight_unit = weight_unit
        self.use_legacy = use_legacy

        self.out_dir = (
            tempfile.TemporaryDirectory(prefix="act_out_").name
            if out_dir is None
            else out_dir
        )

        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir, exist_ok=True)

        # create symlink to latest run
        pathlib.Path(SYMLINK_PATH).unlink(missing_ok=True)
        if not test:  # do not create for tests
            try:
                os.symlink(self.out_dir, SYMLINK_PATH)
            except FileExistsError:
                log.info("Couldn't update symlink. Results may be stale.")

        # load the models for each type of device
        self.ci_model = CIModel(use_legacy=self.use_legacy)
        self.logic_model = LogicModel(
            ci_model=self.ci_model, use_legacy=self.use_legacy
        )
        self.dram_model = DRAMModel(model_file=dram_config)
        self.ssd_model = SSDModel()
        self.hdd_model = HDDModel(model_files=hdd_config)
        self.op_model = OpModel(ci_model=self.ci_model, use_legacy=self.use_legacy)
        self.cap_model = CapacitorModel(model_file=cap_config, ci_model=self.ci_model)
        self.materials_model = MaterialsModel(model_file=materials_config)
        self.ap_model = APModel(model_file=ap_config)
        self.imec_logic_model = IMECLogicModel()
        self.pcb_model = PCBModel()
        self.battery_model = BatteryModel(model_file=battery_config)
        self.manual_model = ManualModel()
        self.tech_scaling_manager = TechScalingManager()

        # placeholder values
        self.op_power = None
        self.op_ci = None
        self.op_year = None
        self.duty_cycle = None
        self.life_cycle = None
        self.bom = None
        self.op_carbon = None

        # metric analyzer and telemetry results
        self.metric_analyzer = None
        self.metric_results = None
        self.start_time, self.end_time = None, None
        self.cost_analyzer = None

        # dashboard attributes
        self.dashboard_uri = None
        self.dashboard_asset = None
        self.spreadsheet_asset = None

        # load the technology scaling results if one is specified
        if scaling_config is not None:
            self.scaling_file = None
            self.scaling_config = scaling_config
        elif scaling_file is not None:
            self.scaling_file = scaling_file
            self.scaling_config = ScalingConfig(
                **load_yaml_with_macros(self.scaling_file)
            )
        else:
            self.scaling_file = None
            self.scaling_config = None

        # generate result data structure
        self.results = ACTResult()

    def get_carbon(
        self,
        bom,
        op_power: pint.Quantity = None,
        op_ci=None,
        op_year=DEFAULT_OP_YEAR,
        duty_cycle: float = 1.0,
        life_cycle=2 * year,
        export_file=None,
    ):
        """Calculate the aggregate carbon cost for this configuration.

        Args:
            bom (BOM): Bill of materials data structure specifying the component lists and parameters.
            op_power (pint.Quantity): Operating power of the device.
            op_ci (str): Operational carbon intensity setting.
            op_year (int): Year for operational carbon intensity lookup.
            duty_cycle (float): Device utilization rate between 0 and 1.
            life_cycle (pint.Quantity): Expected hardware life cycle.
            export_file (str): Output file path for results.

        Returns:
            Carbon: The total carbon emissions for the configuration.
        """

        # record start of analysis for run time regression purposes
        self.start_time = datetime.datetime.now()

        self.op_power = self.results.op_power = resolve_op_power(
            cl_op_power=op_power, bom=bom
        )
        self.op_ci = resolve_op_ci(cl_op_ci=op_ci, bom=bom)
        self.op_year = resolve_op_year(cl_op_year=op_year, bom=bom)
        self.duty_cycle = self.results.duty_cycle = resolve_duty_cycle(
            cl_duty_cycle=duty_cycle, bom=bom
        )
        self.life_cycle = self.results.life_cycle = resolve_life_cycle(
            cl_life_cycle=life_cycle, bom=bom
        )
        self.bom = self.results.bom = bom

        self.bom.set_op_parameters(
            op_ci=self.op_ci,
            op_year=self.op_year,
            duty_cycle=self.duty_cycle,
            life_cycle=self.life_cycle,
            override=False,  # do not override existing parameters
        )
        self.bom.devices[VIRTUAL_POWER_DEVICE] = DeviceData(
            model=ModelType.POWER,
            power=self.op_power,
            op_ci=self.op_ci,
            op_year=self.op_year,
            life_cycle=self.life_cycle,
            duty_cycle=self.duty_cycle,
        )

        # apply the power scaling before carbon analysis
        self.tech_scaling_manager.apply_power_scaling(
            bom, scaling_config=self.scaling_config
        )

        # calculate the total carbon
        carbon_results = self.carbon_analysis(bom)
        self.results.set_carbon_by_device(carbon_results)

        # apply technology scaling if specified
        if self.scaling_config is not None:
            # apply embodied carbon technology scaling
            self.tech_scaling_manager.apply_tech_scaling(self)

            # apply carbon intensity scaling
            apply_ci_scaling(
                act_results=self.results,
                bom=self.bom,
                scaling_config=self.scaling_config,
                ci_model=self.ci_model,
            )

            # re-calculate the result the results data structure
            self.results.recalculate()

        # run metric analysis
        self.metric_analyzer = MetricAnalyzer(act_model=self)
        self.results.metrics = self.metric_analyzer.get_results()
        self.cost_analyzer = CostAnalyzer(act=self)

        # export the results
        self.export_results(export_file)

        # mark the analysis end time
        self.end_time = datetime.datetime.now()

        return self.results.total_carbon

    def carbon_analysis(self, bom):
        """Run carbon analysis for all devices in the bill of materials.

        Args:
            bom (BOM): Bill of materials containing device specifications.

        Returns:
            dict[str, Carbon]: Dictionary mapping device names to their carbon emissions.

        Raises:
            NotImplementedError: If a device model type is not supported.
        """
        devices = bom.devices

        # for each device, run the carbon modeling analysis
        carbon_by_device = dict()

        # for each device item in the list, query the manufacturing cost
        for dname, device_data in devices.items():
            mtype = device_data.model

            # calculate the carbon emissions for silicon devices
            if mtype is ModelType.LOGIC:
                emb_carbon = self.logic_model.get_carbon(device_data)
            elif mtype is ModelType.IMEC_LOGIC:
                emb_carbon = self.imec_logic_model.get_carbon(device_data)
            elif mtype is ModelType.AP:
                emb_carbon = self.ap_model.get_carbon(device_data)
            elif mtype is ModelType.DRAM:
                emb_carbon = self.dram_model.get_carbon(device_data)
            elif mtype is ModelType.FLASH:
                emb_carbon = self.ssd_model.get_carbon(device_data)
            elif mtype is ModelType.HDD:
                emb_carbon = self.hdd_model.get_carbon(device_data)
            elif mtype is ModelType.MANUAL:
                emb_carbon = self.manual_model.get_carbon(device_data)
            elif device_data.model is ModelType.CAPACITOR:
                emb_carbon = self.cap_model.get_carbon(device_data)
            elif device_data.model is ModelType.MATERIALS:
                emb_carbon = self.materials_model.get_carbon(device_data)
            elif device_data.model is ModelType.PCB:
                emb_carbon = self.pcb_model.get_carbon(device_data)
            elif device_data.model is ModelType.BATTERY:
                emb_carbon = self.battery_model.get_carbon(device_data)
            elif device_data.model is ModelType.POWER:
                emb_carbon = Carbon(0 * kg, SourceType.FABRICATION)
            else:
                raise NotImplementedError(
                    f"Silicon model type for {mtype} not implemented. Unable to calculate cost."
                )

            # all devices which have associated power should have operational carbon calculated
            op_carbon = self.op_model.get_carbon(device_data)

            # update the results with the aggregate total
            carbon_by_device[dname] = op_carbon + emb_carbon

        return carbon_by_device

    def export_results(self, export_file: str):
        """Export analysis results to YAML and spreadsheet files.

        Args:
            export_file (str): Output file path for YAML results. Spreadsheet will use same name with .xlsx extension.
        """
        # export the result to yaml report and spreadsheet for auditing
        if export_file is None:
            export_file = f"{self.out_dir}/act_report.yaml"
        xls_file = export_file.replace(".yaml", ".xlsx")

        # yaml asset export
        self.results.export_yaml(export_file=export_file)
        log.info(f"ACT yaml results written to: {export_file}")

        # spread sheet asset export
        self.results.export_spreadsheet(xls_file)
        log.info(f"ACT spreadsheet results written to: {xls_file}")

    def generate_dashboard(self, extra_cards=None, upload_fn=None):
        """Generate the dashboard and optionally upload it.

        Args:
            extra_cards (list): Optional list of additional dashboard cards to include.
            upload_fn (callable): Optional function to upload the dashboard HTML file.
                Should accept a file path and return the upload URL.

        Returns:
            str or None: The upload URL if upload_fn was provided, None otherwise.
        """
        self.dashboard_asset = ACTDashboard(
            act=self,
            out_dir=self.out_dir,
            dashboard_title=self.bom.name,
        )
        self.dashboard_asset.generate_dashboard(extra_cards=extra_cards)

        log.info(f"Dashboard asset written to: {self.dashboard_asset.packed_html_file}")

        if upload_fn is not None:
            return upload_fn(self.dashboard_asset.packed_html_file)

    def __getstate__(self):
        state = self.__dict__.copy()
        if "dashboard_asset" in state:
            del state["dashboard_asset"]
        return state
