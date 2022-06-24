# ACT: Architectural Carbon Modeling Tool

ACT is an carbon modeling tool to enable carbon-aware design space exploration. ACT comprises an analytical, architectural carbon-footprint model
and use-case dependent optimization metrics to estimate the carbon footprint of hardware. The proposed model estimates emissions from hardware manufacturing (i.e., embodied carbon) based on workload characteristics, hardware specifications, semiconductor fab characteristics, and environmental factors.

ACT addresses a crucial gap in quantifying and enabling sustainability-driven hardware design space exploration, and serves as a call-to-action for com-
puter architects to consider sustainability as a first-order citizen, alongside performance, power, and area (PPA).

# Carbon Footprint Modeling
Central to ACT is an analytical, architectural carbon model to estimate operational and embodied carbon. We describe the model below and details can be found in our paper (see "Link to the Paper" below).

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

# Carbon Optimization Metrics
In addition to the architectural carbon model, it is crucial to have use-case dependent carbon optimization metrics to quantitatively explore sustainable system design spaces. ACT proposes four sustainability-driven optimization metrics to aid early design space exploration. Here _C_ stands for embodied carbon, _D_ for delay, and _E_ for energy.

| Metric        | Description   | Use case |
| :-------------: |:-------------:| :-----:|
| $$CDP$$      | Carbon-delay-product | Balance carbon and performance (e.g., sustainable data center) |
| $$CEP$$      | Carbon-energy-product | Balance carbon and energy (e.g., sustainable mobile device) |
| $$C^2EP$$      | Carbon square-energy-product | Sustainable device dominated by embodied carbon |
| $$CE^2P$$      | Carbon-energy squared-product | Sustainable device dominated by operational carbon |


# Getting Started
To get you started quickly, the code is structured to flexibly study various use-cases and easily extend the framework.

1. The top-level is found in ```model.py```. This co-ordinates the underlying embodied architectural carbon model for logic, memory, and storage.
2. The logic model (e.g., application processors) can be found in the ```logic_model.py``` and the ```logic``` directory.
3. The memory model can be found in the ```dram_model.py``` and the ```dram``` directory.
4. The NAND Flash storage model can be found in the ```ssd_model.py``` and the ```ssd``` directory.
5. The HDD storage model can be found in the ```hdd_model.py``` and the ```hdd``` directory.
6. The carbon intensity of different energy sources and geographic locations across the world can be found in ```carbon_intensity```.

Data for the architectural carbon model draw from sustainability literature and industry sources (additional information can be found in our paper, see details below).

The code is built on ```Python 3.7.7``` and no special packages are required.

## Example carbon analyses
As examples we have provided two comparisons with ACT against life cycle analyses (LCA's). The first with Fairphone 3 and the second with the Dell R740 LCA's.

# Link to the Paper
To read the paper please visit this [link](https://github.com/fairinternal/ACT)


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
