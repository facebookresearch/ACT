# ACT: Architectural Carbon Modeling Tool

Version: 2.0 <br>
README Last Updated: 2/17/2025

ACT is an carbon modeling tool to enable carbon-aware design space exploration.
ACT comprises an analytical, architectural carbon-footprint model and use-case dependent optimization metrics to estimate the carbon footprint of hardware.
The proposed model estimates emissions from hardware manufacturing (i.e., embodied carbon) based on workload characteristics, hardware specifications, semiconductor fab characteristics, and environmental factors.

ACT addresses a crucial gap in quantifying and enabling sustainability-driven hardware design space exploration, and serves as a call-to-action for computer architects to consider sustainability as a first-order citizen, alongside performance, power, and area (PPA).
If you use ACT for your research, please consider contributing the resulting system specification for your carbon model analysis to the bill of materials directory (`ACT/act/boms`).

## Quick Start

To get started, first clone [ACT](https://github.com/facebookresearch/ACT) and make sure you have the following third-party Python dependencies:
* [pint](https://pint.readthedocs.io/en/stable/) - `pip install pint`
* [pyyaml](https://pypi.org/project/PyYAML/) - `pip install pyyaml`
* Make sure you have Python 3.12.9
ACT can be used either as a standalone binary or an API where you can program your codebase and use cases against.
The code is built on `Python 3.12.9`.

### Command Line

To use ACT as a standalone binary tool:

1. Go to the ACT root directory
2. From the command line, run `act_model.py -m boms/dellr740.yaml` which should run an existing specification for the Dell power edge server
3. This should export the results to a report yaml file where you can inspect the results

For the full list of command line arguments, use `python -m act.act_model --help`.

### Python API

To program against ACT in your own script:
1. Go to the ACT root directory
2. In your python script, import ACTModel which is the top level Python class from act_model.py
3. Instantiate ACTModel which will instantiate and load all of the submodels
4. Generate a bill of materials instance BOM from bom.py which specifies the resources for the device you want to study
5. Call the ACTModel `get_carbon()` function with the bill of materials instance as well as other parameters (see the `get_carbon()` function)
6. This should return a dictionary of the carbon results by each component in the system

## Bill of Materials Specification

For complex systems, we recommend using the ACT bill of materials yaml specification to specify your system architecture.
The bill of materials specification is composed of three main sections:
1. `silicon`: Any silicon systems like logic, DRAM, SSD, HDD, etc.
2. `materials`: Materials required for the frame and enclosure of the system
3. `passives`: Passive components (ex., capacitors, etc.)

A sample bill of materials file is shown below:
```
name: Test bill of material
passives:
  cap0:
    category: capacitor
    type: mlcc
    quantity: 2
    weight: 0.03 mg
silicon:
  dut:
    area: 10 mm2
    fab_yield: 0.87
    process: 14nm
    n_ics: 1
    fab_ci: taiwan
  dram:
    model: dram
    capacity: 1 GB
    fab_yield: 0.9
    process: ddr4_10nm
  ssd:
    model: flash
    capacity: 2 TB
    fab_yield: 0.88
    process: nand_10nm
  hdd:
    model: hdd
    capacity: 1 TB
    fab_yield: 0.92
    process: BarraCuda
materials:
  fasteners:
    category: enclosure
    type: steel
    weight: 0.6 g
  pcb:
    category: pcb
    area: 10 cm2
    layers: 4
  battery:
    category: battery
    capacity: 5000 mWh
```

You can either write your own similar bill of materials or start from one of the existing bill of materials in the `boms` directory.
Once you have your bill of materials specification, you can run it with ACT using `python -m act.act_model -m <your bom yaml>`.
For instance, `python -m act.act_model -m act/boms/dellr740.yaml` will run one of the stock Dell R740 models.

## Codebase Structure

The top level binary is ACTModel.py which orchestrates the calculations across the underlying embodied architectural carbon model for logic, memory, storage, etc.

ACT currently supports the following models:
* `logic_model.py`: Application processor and digital logic embodied carbon model
* `dram_model.py`: DRAM embodied carbon capacity-based models
* `ssd_model.py`: SSD embodied carbon capacity-based models
* `hdd_model.py`: HDD embodied carbon capacity-based models
* `op_model.py`: Operational emissions model
* `cap_model.py`: Capacitor manufacturing embodied carbon model
* `materials_model.py`: Frame and enclosure materials embodied carbon model
* `pcb_model.py`: Printed circuit board area-based embodied carbon model
* `battery_model.py`: Battery capacity-based embodied carbon model

Data for the architectural carbon model draw from sustainability literature and industry sources (additional information can be found in [our paper](https://dl.acm.org/doi/10.1145/3470496.3527408), see details below).

## Carbon Footprint Modeling Details

Central to ACT is an analytical, architectural carbon model to estimate operational and embodied carbon.
We describe the model below and details can be found in our [paper](https://dl.acm.org/doi/10.1145/3470496.3527408).

At the highest level the analytical carbon model combines operational and embodied carbon. As embodied carbon is generated at design and manufacturing time, we amortize emissions across the duration of a software application (T) over the lifetime of a hardware platform (LT).

$$CF = OP_{CF} + \frac{T}{LT} \times E_{CF}$$

The operational carbon owes to the product of the carbon intensity of energy consumed and the energy expenditure of running an application on hardware device.

$$OP_{CF} = CI_{use} \times Energy$$

The embodied carbon owes to both packaging overhead and the embodied carbon of individual hardware components. For packaging overheads we multiply the number of integrated circuits (Nr) with a packaging footprint (Kr). The embodied carbon of all integrated circuits (e.g., application processors and SoC's, DRAM memory, SSD storage, HDD storage) are aggregated.

$$E_{CF} = N_r K_r + \sum_{r}^{SoC, DRAM, SSD, HDD} E_r$$

The embodied footprint of application processors and SoC's depends on the die area, carbon intensity of the energy consumed by the fab and energy consumed per unit area manufactured, the GHG footprint of gasses and chemicals per unit area manufactured, the footprint of procuruing raw materials per unit area, and fabrication yield.

$$E_{SoC} = Area \times CPA$$

$$E_{SoC} = Area \times \frac{CI_{fab} \times EPA + GPA + MPA}{Y}$$

Finally, the embodied carbon of the memory and storage devices depends on the carbon per storage intensity and the storage capacity of the modules.

$$E_{DRAM} = CPS_{DRAM} \times Capacity_{DRAM}$$

$$E_{HDD} = CPS_{HDD} \times Capacity_{HDD}$$

$$E_{SSD} = CPS_{SSD} \times Capacity_{SSD}$$

Refer to the [original paper](https://dl.acm.org/doi/abs/10.1145/3470496.3527408) for the details.

## Carbon Optimization Metrics

In addition to the architectural carbon model, it is crucial to have use-case dependent carbon optimization metrics to quantitatively explore sustainable system design spaces. ACT proposes four sustainability-driven optimization metrics to aid early design space exploration. Here _C_ stands for embodied carbon, _D_ for delay, and _E_ for energy.

| Metric        | Description   | Use case |
| :-------------: |:-------------:| :-----:|
| $$CDP$$      | Carbon-delay-product | Balance carbon and performance (e.g., sustainable data center) |
| $$CEP$$      | Carbon-energy-product | Balance carbon and energy (e.g., sustainable mobile device) |
| $$C^2EP$$      | Carbon square-energy-product | Sustainable device dominated by embodied carbon |
| $$CE^2P$$      | Carbon-energy squared-product | Sustainable device dominated by operational carbon |


## Example Carbon Analyses

As examples we have provided two comparisons with ACT against life cycle analyses (LCA's). The first with Fairphone 3 and the second with the Dell R740 LCA's.
You can find some of the sample bill of materials for these analyses in the `act/boms` directory.

# Link to the Paper
To read the paper please visit this [link](https://dl.acm.org/doi/abs/10.1145/3470496.3527408)


# Citation
If you use `ACT`, please cite us:

```
@inproceedings{GuptaACT2022,
author = {Gupta, Udit and Elgamal, Mariam and Hills, Gage and Wei, Gu-Yeon and Lee, Hsien-Hsin S. and Brooks, David and Wu, Carole-Jean},
title = {ACT: Designing Sustainable Computer Systems with an Architectural Carbon Modeling Tool},
year = {2022},
isbn = {9781450386104},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3470496.3527408},
doi = {10.1145/3470496.3527408},
abstract = {Given the performance and efficiency optimizations realized by the computer systems and architecture community over the last decades, the dominating source of computing's carbon footprint is shifting from operational emissions to embodied emissions. These embodied emissions owe to hardware manufacturing and infrastructure-related activities. Despite the rising embodied emissions, there is a distinct lack of architectural modeling tools to quantify and optimize the end-to-end carbon footprint of computing. This work proposes ACT, an architectural carbon footprint modeling framework, to enable carbon characterization and sustainability-driven early design space exploration. Using ACT we demonstrate optimizing hardware for carbon yields distinct solutions compared to optimizing for performance and efficiency. We construct use cases, based on the three tenets of sustainable design---Reduce, Reuse, Recycle---to highlight future methods that enable strong performance and efficiency scaling in an environmentally sustainable manner.},
booktitle = {Proceedings of the 49th Annual International Symposium on Computer Architecture},
pages = {784–799},
numpages = {16},
keywords = {energy, sustainable computing, computer architecture, mobile, manufacturing},
location = {New York, New York},
series = {ISCA '22}
}


```

# License
ACT is MIT licensed, as found in the LICENSE file.
