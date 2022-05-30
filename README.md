# ACT: Architectural Carbon Modeling Tool

ACT is an carbon modeling tool to enable carbon-aware design space exploration. ACT comprises an analytical, architectural carbon-footprint model
and use-case dependent optimization metrics to estimate the carbon footprint of hardware. The proposed model estimates emissions from hardware manufacturing (i.e., embodied carbon) based on workload characteristics, hardware specifications, semiconductor fab characteristics, and environmental factors.

ACT addresses a crucial gap in quantifying and enabling sustainability-driven hardware design space exploration, and serves as a call-to-action for com-
puter architects to consider sustainability as a first-order citizen, alongside performance, power, and area (PPA).

# Carbon Footprint Modeling
Central to ACT is an analytical, architectural carbon model to estimate operational and embodied carbon. We describe the model below and details can be found in our paper (see "Link to the Paper" below).

At the highest level the analytical carbon model combines operational and embodied carbon. As embodied carbon is generated at design and manufacturing time, we amortize emissions across the duration of a software application (T) over the lifetime of a hardware platform (LT).
<p align="center">
<img src="https://latex.codecogs.com/svg.image?CF&space;=&space;OP_{CF}&space;&plus;&space;\frac{T}{LT}&space;\times&space;E_{CF}" >
</p>

The operational carbon owes to the product of the carbon intensity of energy consumed and the energy expenditure of running an application on hardware device.
<p align="center">
<img src="https://latex.codecogs.com/svg.image?OP_{CF}&space;=&space;CI_{use}&space;\times&space;Energy">
</p>

The embodied carbon owes to both packaging overhead and the embodied carbon of individual hardware components. For packaging overheads we multiply the number of integrated circuits (Nr) with a packaging footprint (Kr). The embodied carbon of all integrated circuits (e.g., application processors and SoC's, DRAM memory, SSD storage, HDD storage) are aggregated.
<p align="center">
<img src="https://latex.codecogs.com/svg.image?E_{CF}&space;=&space;N_r&space;K_r&space;&plus;&space;\sum_{r}^{SoC,&space;DRAM,&space;SSD,&space;HDD}&space;E_r">
</p>

The embodied footprint of application processors and SoC's depends on the die area, carbon intensity of the energy consumed by the fab and energy consumed per unit area manufactured, the GHG footprint of gasses and chemicals per unit area manufactured, the footprint of procuruing raw materials per unit area, and fabrication yield.
<p align="center">
<img src="https://latex.codecogs.com/svg.image?E_{SoC}&space;=&space;Area&space;\times&space;CPA">
</p>

<p align="center">
<img src="https://latex.codecogs.com/svg.image?E_{SoC}&space;=&space;Area&space;\times&space;\frac{CI_{fab}&space;\times&space;EPA&space;&plus;&space;GPA&space;&plus;&space;MPA}{Y}">
</p>

Finally, the embodied carbon of the memory and storage devices depends on the carbon per storage intensity and the storage capacity of the modules.


<p align="center">
<img src="https://latex.codecogs.com/svg.image?E_{DRAM}&space;=&space;CPS_{DRAM}&space;\times&space;Capacity_{DRAM}">
</p>

<p align="center">
<img src="https://latex.codecogs.com/svg.image?E_{HDD}&space;=&space;CPS_{HDD}&space;\times&space;Capacity_{HDD}">
</p>

<p align="center">
<img src="https://latex.codecogs.com/svg.image?E_{SSD}&space;=&space;CPS_{SSD}&space;\times&space;Capacity_{SSD}">
</p>

# Carbon Optimization Metrics
In addition to the architectural carbon model, it is crucial to have use-case dependent carbon optimization metrics to quantitatively explore sustainable system design spaces. ACT proposes four sustainability-driven optimization metrics to aid early design space exploration. Here _C_ stands for embodied carbon, _D_ for delay, and _E_ for energy.

| Metric        | Description   | Use case |
| :-------------: |:-------------:| :-----:|
| CDP      | Carbon-delay-product | Balance carbon and performance (e.g., sustainable data center) |
| CEP      | Carbon-energy-product | Balance carbon and energy (e.g., sustainable mobile device) |
| C^2EP      | Carbon square-energy-product | Sustainable device dominated by embodied carbon |
| CE^2P      | Carbon-energy squared-product | Sustainable device dominated by operational carbon |


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
   @conference{Gupta2022,
   title = {ACT: Designing Sustainable Computer Systems With An Architectural Carbon Modeling Tool},
   author = {Udit Gupta, Mariam Elgamal, Gage Hills, Gu-Yeon Wei, Hsien-Hsin S. Lee, David Brooks, Carole-Jean Wu},
   url = {},
   year = {2022},
   date = {2022-06-01},
   publisher = {The 49th IEEE/ACM International Symposium on Computer Architecture (ISCA 2022)},
   keywords = {Computer Architecture, sustainable computing, mobile, energy, manufacturing},
   pubstate = {published},
   tppubtype = {conference}
   }
```

# License
ACT is MIT licensed, as found in the LICENSE file.
