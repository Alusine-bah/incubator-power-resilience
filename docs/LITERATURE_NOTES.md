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

**Not in this paper:** incubator made in 2006, empty hood, steady state after about 57 minutes. All three are confirmed in entry 2.

**Limits to remember:** one incubator, one operating point (36 °C inside, 25 °C outside), measured in a lab in Turkey.

## 2. Yeler and Koseoglu (2022)

**Citation:** Yeler, O., Koseoglu, M. F. (2022). Energy efficiency and transient-steady state performance comparison of a resistance infant incubator and an improved thermoelectric infant incubator. *Engineering Science and Technology, an International Journal*, 31, 101055. (Open access.)

**Checked:** 2026-11-15, against the published PDF.

**What the paper is about:** the same team compares the original resistance incubator with their thermoelectric version, measuring warm-up, steady-state power, air flows, noise and the response when the hood is opened with a manikin inside.

**What it confirms for this project:**

| Our input | What the paper says |
| --- | --- |
| Device: AMS Amenity XP, made in 2006 | "AMS Amenity XP premature infant incubator manufactured in 2006 was purchased" |
| Tests with an empty hood | The steady-state results come from "36 °C experiments without manikin" |
| Steady state after about 57 min | The resistance system "reaches steady state around 57 min" |
| 168 W average electrical power in steady state | The resistance system "consumes an average of 168 W of electrical power in the steady state" |
| Air flows 0.002293 kg/s fresh, 0.005555 kg/s mixed; hood air 0.0929 m/s | Same values reported in the air-flow measurements |

**Note:** 168 W (electrical, this paper) against 162.95 W (heat, 2020 paper). We read the difference of about 5 W as fan and controls; that is our inference, not the authors' statement.

**Useful later (not used yet):**
- Steady-state results at several set temperatures from 38 °C to 30 °C, partly in a supplementary table. These could show whether heat loss stays constant across set temperatures. The supplementary file has not been read.
- A test where the hood is opened for 1 minute with a warm-water manikin (36.7 °C core) inside, with core and skin temperatures recorded. This is real disturbance data that could help Paper 1 (detecting an open hood or porthole).

## 3. Mestyan, Jarai and Fekete (1968)

**Citation:** Mestyan, J., Jarai, I., Fekete, M. (1968). The total energy expenditure and its components in premature infants maintained under different nursing and environmental conditions. *Pediatric Research*, 2(3), 161-171.

**Correction:** this paper is often cited as "Fekete 1968", but the first author is J. Mestyan. Cite it as Mestyan et al. (1968).

**Checked:** 2026-11-15, against the published PDF.

**What the paper is about:** oxygen consumption, and so heat production, measured for several hours in 23 premature infants (birth weight 1100 to 2120 g, aged 2 to 31 days) under four care conditions.

**What it supports for this project:** baby heat production of 1.9 to 2.8 W/kg (our default 2.0 W/kg).

| Condition (from the paper) | Infants | Heat production, kcal/kg/day | W/kg (our conversion) |
| --- | --- | --- | --- |
| Incubator at 33 to 36 °C (neutral), human milk, basal | 9 | 35.4 ± 5.4 | 1.71 |
| Same, total over the observation | 9 | 44.2 ± 7.4 | 2.14 |
| Incubator at 33 to 36 °C (neutral), formula, basal | 4 | 39.7 ± 2.6 | 1.92 |
| Same, total over the observation | 4 | 55.0 ± 4.0 | 2.66 |
| Swaddled in a room at 20 to 22 °C, total | 5 | 58.3 | 2.82 |
| Unclothed at 28 to 29 °C, total | 5 or 6 (the paper gives both) | 80 | 3.87 |

Conversion: 1 kcal/kg/day = 4184 J / 86,400 s = 0.0484 W/kg.

**Reading:** our model keeps the baby in a neutral incubator, so the first four rows apply: 1.7 to 2.7 W/kg. Our range of 1.9 to 2.8 W/kg sits inside or just above that, and our default 2.0 W/kg is close to the total for breast-fed infants (2.14). The last two rows show that a baby in a cooler environment produces more heat, which our model does not include.

**Limits to remember:** a small study (23 infants), from Hungary in the 1960s, using the measuring methods of the time; all infants weighed 1100 g or more, so values for 500 to 1000 g babies are an extrapolation.
