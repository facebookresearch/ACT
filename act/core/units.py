# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Defines pint unit constants
- To make quality of life less bad, this file defines a bunch of units using the pint library
- Add any other units that you need here which may be missing
- Group units that measure the same quantity together
- All prefixes < 1 should be lower case
- All prefixes > 1 should be upper case
- If you need 2^10 instead of 10^3 units, add the "i" to the prefix (ex., GiB)
- This file defines the units as variable to provide a short hand
- Most of these variables are already in the UnitRegistry but some may not be
"""

import pint

units = pint.UnitRegistry()
pint.set_application_registry(units)  # required for multiprocessing

# Time units
fs = units("femtosecond")
ps = units("picosecond")
ns = units("nanosecond")
us = units("microsecond")
ms = units("millisecond")
s = units("second")
minute = units("minute")
hour = units("hour")
hr = hour
day = units("day")
week = units("week")
month = units("month")
year = units("year")

# Power units
fW = units("femtowatt")
pW = units("picowatt")
nW = units("nanowatt")
uW = units("microwatt")
mW = units("milliwatt")
W = units("watt")
KW = units("kilowatt")
MW = units("megawatt")
GW = units("gigawatt")
TW = units("terawatt")

# Energy units
fJ = units("femtojoule")
pJ = units("picojoule")
nJ = units("nanojoule")
uJ = units("microjoule")
mJ = units("millijoule")
J = units("joule")
KJ = units("kilojoule")
MJ = units("megajoule")
GJ = units("gigajoule")
TJ = units("terajoule")

# shorthand not defined in registry, define it
units.define("mWh = milliwatt hour")
units.define("kWh = kilowatt hour")
mWh = units("milliwatt hour")
kWh = units("kilowatt hour")

# Memory units
bit = units("bit")
byte = units("byte")
Kb = units("kilobit")
KB = units("kilobyte")
KiB = units("kibibyte")
Mb = units("megabit")
MB = units("megabyte")
MiB = units("mebibyte")
Gb = units("gigabit")
GB = units("gigabyte")
GiB = units("gibibyte")
Tb = units("terabit")
TB = units("terabyte")
TiB = units("tebibyte")
Eb = units("exabit")
EB = units("exabyte")
EiB = units("exabyte")
Pb = units("petabit")
PB = units("petabyte")
PiB = units("pebibyte")

# Bandwidth units
bps = units("bit/s")
Bps = units("byte/s")
Kbps = units("kilobit/s")
KBps = units("kilobyte/s")
KiBps = units("kibibyte/s")
Mbps = units("megabit/s")
MBps = units("megabyte/s")
MiBps = units("mebibyte/s")
Gbps = units("gigabit/s")
GBps = units("gigabyte/s")
GiBps = units("gibibyte/s")
Tbps = units("terabit/s")
TBps = units("terabyte/s")
TiBps = units("tebibyte/s")
Ebps = units("exabit/s")
EBps = units("exabyte/s")
EiBps = units("exbibyte/s")
Pbps = units("petabit/s")
PBps = units("petabyte/s")
PiBps = units("pebibyte/s")

# Compute units
FLOPS = units("Hz")
kFLOPS = units("kHz")
MFLOPS = units("MHz")
GFLOPS = units("GHz")
TFLOPS = units("THz")
PFLOPS = units("PHz")
EFLOPS = units("EHz")
OPS = units("Hz")
kOPS = units("kHz")
MOPS = units("MHz")
GOPS = units("GHz")
TOPS = units("THz")
POPS = units("PHz")
EOPS = units("EHz")


# pint does not recognize this shorthand by default so it needs to be registered
units.define("bps = bit /s")
units.define("Bps = byte / s")
units.define("Kbps = kilobits / s")
units.define("KBps = kilobyte / s")
units.define("KiBps = kibibyte / s")
units.define("Mbps = megabits / s")
units.define("MBps = megabyte / s")
units.define("MiBps = mebibyte / s")
units.define("Gbps = gigabits / s")
units.define("GBps = gigabyte / s")
units.define("GiBps = gibibyte / s")
units.define("Tbps = terabits / s")
units.define("TBps = terabyte / s")
units.define("TiBps = tebibyte / s")
units.define("Ebps = exabits / s")
units.define("EBps = exabyte / s")
units.define("EiBps = exbibyte / s")
units.define("Pbps = petabits / s")
units.define("PBps = petabyte / s")
units.define("PiBps = pebibyte / s")

units.define("FLOPS = Hz")
units.define("kFLOPS = kHz")
units.define("MFLOPS = MHz")
units.define("GFLOPS = GHz")
units.define("TFLOPS = THz")
units.define("PFLOPS = PHz")
units.define("EFLOPS = EHz")
units.define("OPS = Hz")
units.define("kOPS = kHz")
units.define("MOPS = MHz")
units.define("GOPS = GHz")
units.define("TOPS = THz")
units.define("POPS = PHz")
units.define("EOPS = EHz")

# Frequency units
Hz = units("Hz")
kHz = units("kHz")
MHz = units("MHz")
GHz = units("GHz")
THz = units("THz")

# voltage
nV = units("nanovolt")
uV = units("microvolt")
mV = units("millivolt")
V = units("volt")
KV = units("kilovolt")
MV = units("megavolt")
GV = units("gigavolt")

nA = units("nanoamp")
uA = units("microamp")
mA = units("milliamp")
A = units("amp")
KA = units("kiloamp")
MA = units("megaamp")
GA = units("gigaamp")

# temperature
C = units("degC")
F = units("degF")

# area units for silicon die sizes
units.define("um2 = um ** 2")
units.define("mm2 = mm ** 2")
units.define("cm2 = cm ** 2")
units.define("m2 = m ** 2")

um2 = units("um ** 2")
mm2 = units("mm ** 2")
cm2 = units("cm ** 2")
m2 = units("m ** 2")

# weight for emissions estimates
g = units("g")
kg = units("kg")
ton = units("metric_ton")
Mton = 1000000 * ton

# distance
m = units("meter")
km = units("kilometer")
mi = units("mile")
