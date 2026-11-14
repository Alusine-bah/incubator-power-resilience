# Literature notes

One entry per paper, added when the paper itself has been read. Each entry says what we checked, page by page, and what it supports in this project.

## 1. Yeler and Koseoglu (2020)

**Citation:** Yeler, O., Koseoglu, M. F. (2020). Optimization and experimental validation of a modular thermoelectric heat pump system for a premature baby incubator. *Journal of Electronic Materials*, 49(6), 4053-4066. https://doi.org/10.1007/s11664-020-08082-1

**Checked:** 2026-11-15, against the published PDF.

**What the paper is about:** replacing the resistance heater of a commercial incubator with a thermoelectric heat pump. To size it, the authors measured how much heat the original incubator needs.

**What it confirms for this project:**

| Our input | What the paper says | Page |
| --- | --- | --- |
| Steady heat need 162.95 W at 36 °C hood air, 25 °C ambient | "the Amenity XP incubator needs an average 162.95 W of heat power in order to operate in a steady state where the ambient temperature is 25°C and the hood air temperature is 36°C" | 4063 |
| Device: AMS Amenity XP, resistance heater | Commercial "(resistance) incubator system (AMS Amenity XP)" | 4063 |
| Maximum heater power 368 W during warm-up | The resistance heater "consumes 368 W of electrical energy at maximum power" while raising the hood to the set temperature | 4064 |
| Measurement method | 18 T-type thermocouples at points specified in EN 60601-2-19; electrical power also measured | 4064 |

**Used in the project for:** heat loss UA = 162.95 / (36 - 25) = 14.8 W/°C (our arithmetic), and heater power around 350 to 400 W.

**Not in this paper (still to check):** incubator made in 2006, empty hood, steady state reached after about 57 minutes. These are probably in Yeler and Koseoglu (2022).

**Limits to remember:** one incubator, one operating point (36 °C inside, 25 °C outside), measured in a lab in Turkey.
