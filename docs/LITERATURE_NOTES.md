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

## 4. Sauer, Dane and Visser (1984)

**Citation:** Sauer, P. J. J., Dane, H. J., Visser, H. K. A. (1984). New standards for neutral thermal environment of healthy very low birthweight infants in week one of life. *Archives of Disease in Childhood*, 59(1), 18-22. Free on PubMed Central (PMC1628424).

**Checked:** 2026-11-15, against the PDF from PubMed Central.

**What the paper is about:** the incubator temperature at which a preterm baby keeps a core temperature of 36.7 to 37.3 °C without warming or cooling (the "neutral temperature"). 25 studies in 14 infants in the first week (29 to 34 weeks' gestation), and 78 measurements in 27 infants after the first week (birth weight 0.81 to 1.85 kg).

**The two equations it gives:**

- First week: neutral temperature = 36.6 - 0.34 x (gestational age - 30 weeks) - 0.28 x age in days. Standard deviation 0.7 °C.
- After the first week: neutral temperature = 36 - 1.4 x weight in kg - 0.03 x age in days. Standard deviation 0.65 °C.

Both apply only when the incubator walls are as warm as the air and the air has a dew point of 18 °C. With cooler walls the air must be warmer (neutral = 0.4 x air + 0.6 x wall); with more humid air the neutral temperature is lower.

**Compared with our setpoints (from hospital guidelines):**

| Case | Sauer et al. | Our model |
| --- | --- | --- |
| 1 kg, day 7 | 34.4 °C | 34.9 °C |
| 2 kg, day 7 | 33.0 °C | 33.5 °C |
| 33 weeks' gestation, day 1 | 35.3 °C | 33.5 °C (if about 2 kg) |
| 33 weeks' gestation, day 7 | 33.6 °C | 33.5 °C |

(Values in the Sauer column are our arithmetic from the equations.)

**Reading:** after the first week our setpoints agree with Sauer within about 0.5 °C, inside the paper's own scatter. In the first few days Sauer gives higher values, up to about 2 °C higher. A higher setpoint means more heat loss: at a 22 °C room, 35.0 °C instead of 33.5 °C raises the heater's steady load by about 13 percent (our arithmetic). So for babies in their first days, our battery sizes may be somewhat low. This is a possible model change to discuss at the build stage; nothing has been changed yet.

**Limits to remember:** small study from the Netherlands; healthy infants only; values above 2 kg are extrapolated; test conditions (equal wall and air temperature, dew point 18 °C) differ from most real incubators.

## 5. Miles et al. (2025)

**Citation:** Miles, S. B., Mughuma, J. M., Moner-Girona, M., Kammen, D. M., Kwong, L. H. (2025). The power of health in the Democratic Republic of the Congo: Electricity quality and reliability in medical facilities of North Kivu Province. *Applied Energy*, 401, 126830.

**Checked:** 2026-11-15, against the published PDF.

**What the paper is about:** cellular-connected sensors recorded outages, voltage and frequency at 25 health facilities in North Kivu, DR Congo, from 2022 to October 2024 (about 29 months).

**What it confirms for this project:**

| Our input | What the paper says |
| --- | --- |
| Outages a day at DR Congo facilities | Mean 0.67 a day across the 25 facilities (range 0 to 2.04) |
| Typical outage time about 2 h | 2.01 h (range 0.03 to 10.9 h), see the note below |
| Differences by facility type | General referral hospitals 1.17 h, referral health centres 3.80 h, health centres 3.91 h, private hospitals 0.16 h (Table 4) |
| Uptime and voltage | Mean uptime 93.2 percent (46.7 to 100); voltage within ±10 percent of 230 V for 73.9 percent of the time |

**Important note on what "2.01 h" means:** the paper defines it as the median *daily* outage time (hours per day) on days with at least one outage, averaged across facilities (Methods and the Table 4 heading). It is not the length of each single outage. Because most outage days have only one outage (0.67 a day on average), the two are similar, but not identical. In our project the outage length is our own chosen distribution (median 1.5 h, limited to 0.25 to 11 h), which this paper supports as a reasonable range rather than as a direct measurement.

**Something to check later:** the paper summarises the Sierra Leone study (Wall and Odero, its reference 16) as "an average of 3 outages per day, each with a median duration of 3 h". Our notes from the Wall et al. report give 0.6 to 3.1 outages a day across 15 facilities. These may describe different facilities or summaries; we should check the Wall report directly.

**Limits to remember:** one province of one country; facilities were selected, not random; the facilities with solar-only systems had almost no outages, so results depend strongly on how each facility is supplied.

## 6. Wall et al. (2024)

**Citation:** Wall, A., Osunmuyiwa, O., Flaspohler, G., Odero, M., Goode, J., Klugman, N., Podolsky, M. (2024). *On the path to sustainable health electrification? Uncovering power quality and reliability challenges at electrified health facilities in Sierra Leone.* International Growth Centre, Final report SLE-20186. Free online. This is a report, not a peer-reviewed paper.

**Checked:** 2026-11-15, against the PDF.

**What the report is about:** nLine GridWatch sensors in wall outlets at 15 health facilities in Sierra Leone (seven hospitals, seven community health centres, one health post). The analysis period is 20 July to 31 August 2023 (six weeks).

**What it confirms for this project:**

| Our input | What the report says |
| --- | --- |
| 0.6 to 3.1 outages a day | Fewest at Ola During (0.63 a day), most at Wellington CHC (3.07 a day) |
| 0.03 to 18 hours a day without power | Lowest Ola During (0.03 h a day), highest Bonthe Government Hospital (18.43 h a day); body text and appendix table agree |
| Voltage as low as 127 V (0.55 of 230 V) | Wellington CHC spent on average 12.78 h a day outside the normal range, "dropping as low as 127 V at times" |
| Staff report power too weak for a fan | Wellington's Community Health Officer: grid power "is not able to even turn the fan or turn on [the] computer" |

**Settled questions:**
- The executive summary says "as much as nine hours" a day without power, but the results and the appendix table give 18.43 h for Bonthe. We use the detailed results.
- Miles et al. (2025) summarise this study as "3 outages per day, each with a median duration of 3 h". That is not in this report: 3.07 a day is the single worst facility, and the report gives hours per day, not the length of each outage. Dividing Wellington's 6.40 h a day by its 3.07 outages gives about 2 h per outage (our arithmetic).

**Limits to remember:**
- Wet season only. The report says the data "is only representative of PQR for the wet season months of July and August"; the main hydro plant gives 40 to 50 MW in the wet season but only 10 to 15 MW in the dry season, so dry-season outages may be worse.
- "Poverty outages" (a facility unable to pay for grid power or fuel) were removed. At Waterloo CHC the real situation was 24 hours a day without power from 28 July, against the 6.63 h a day in the results.
- Grey literature: a report, not peer-reviewed. For key numbers we pair it with Miles et al. (2025).

## 7. World Health Organization (1997)

**Citation:** World Health Organization (1997). *Thermal Protection of the Newborn: A Practical Guide.* WHO/RHT/MSM/97.2. Geneva: WHO. Free online.

**Checked:** 2026-11-15, against the PDF.

**What it is:** WHO's practical guide on keeping newborns warm: definitions of hypothermia, how to measure temperature, how to rewarm, and the use of incubators and other warming methods.

**What it confirms for this project (the temperature classes in our README):**

| Baby's temperature | WHO class | WHO wording |
| --- | --- | --- |
| 36.5 to 37.5 °C | Normal | "normal body temperature of 36.5—37.5°C" |
| 36.0 to 36.4 °C | Cold stress (mild hypothermia) | "Cause for concern" |
| 32.0 to 35.9 °C | Moderate hypothermia | "Danger, warm baby" |
| Below 32 °C | Severe hypothermia | "Outlook grave, skilled care urgently" |

**Correction made:** an older line in PARAMETERS.md described WHO cold stress as 36.0 to 32.0 °C. That was wrong; cold stress is 36.0 to 36.4 °C, and 32.0 to 35.9 °C is moderate hypothermia.

**Other points useful for the project:**
- Why it matters: the guide states that "hypothermia, even if moderate, is associated with an increased risk of death in low birth weight newborns".
- Measurement: WHO prefers axillary (under-arm) temperature for routine checks and rectal temperature when hypothermia is suspected, because it is closer to core temperature. Our model gives core temperature, so comparisons with these classes are approximate (the README already says this).
- Room temperature: "If the room temperature is below 25°C (77°F), it is often impossible to compensate for radiant heat loss by increasing the air temperature inside the incubator." Our model does not include radiant loss to cold incubator walls, so at our default 22 °C room it may be optimistic about how warm the baby stays. This supports the finding that room temperature matters most, and it is a limitation to state.

**Limits to remember:** a practical guide from 1997, not a research study; the classes are clinical conventions based on axillary or rectal temperature.

## 8. Kebede et al. (2021)

**Citation:** Kebede, F. S., Olivier, J.-C., Bourguet, S., Machmoum, M. (2021). Reliability evaluation of renewable power systems through distribution network power outage modelling. *Energies*, 14(11), 3225. https://doi.org/10.3390/en14113225 (Open access.)

**Checked:** 2026-11-15, against the published PDF.

**What the paper is about:** sizing a solar PV and battery system for a grid-connected building on an unreliable grid. The case study is a university building in Addis Ababa, Ethiopia, with its load measured by a power analyser and five years of recorded grid outages. A genetic algorithm (NSGA-II) finds the cheapest PV and battery sizes for each reliability level, measured by the loss of power supply probability (LPSP). Outages are also simulated with a Markov model and a Weibull model to test the designs on many outage scenarios. Time step: 1 minute.

**Why it matters for us:** it is the closest earlier method to our grid-with-outages-plus-solar sizing. We must cite it and say how ours differs.

**Findings that agree with ours:**
- Saturation: "the LPSP barely responded to PV area and battery sizes after certain values". We found the same: little benefit beyond about 1 kWp.
- Night outages drive the battery: "The longer the outage duration and/or if it occurs at night when there is no PV production, the higher the battery size."
- Long outages cost the most: longer outage duration makes the LPSP rise and demands larger systems.

**How our work differs:**

| | Kebede et al. (2021) | Our project |
| --- | --- | --- |
| Load | Measured building load (one month) | Incubator heater from a heat-balance model of the incubator and baby |
| Outage data | Five years recorded at one building in Addis Ababa | Measured statistics from health facilities in Sierra Leone and DR Congo, turned into random outages |
| Solar data | One site | Ten years of hourly PVGIS data at five sites |
| Goal | Cheapest system for a chosen reliability level | Smallest battery for zero hours without power, and the trade-off curves |
| Cost | Included (cost of energy) | Not included |
| Time step | 1 minute | 1 hour (checked against our 1-second model) |

**Ideas we could use later:** reporting reliability as LPSP (the standard measure) as well as "hours without power"; Weibull or Markov outage models as an alternative to our lognormal outage lengths; adding cost.

**Limits to remember:** one building in one city; a university building load, not medical equipment.

## 9. Rincon Casado et al. (2021)

**Citation:** Rincon Casado, A., Larrode-Diaz, M., Fernandez Zacarias, F., Hernandez Molina, R. (2021). Experimental and computational model for a neonatal incubator with thermoelectric conditioning system. *Energies*, 14(17), 5278. https://doi.org/10.3390/en14175278 (Open access.)

**Checked:** 2026-11-15, against the published PDF.

**What the paper is about:** a commercial incubator (Ohio Care Plus 3000) fitted with a thermoelectric (Peltier) heater, a simple node-and-resistance thermal model of it (air, mattress surface and heater chamber; no baby), and tests in a temperature-controlled room to measure the model's resistances and check the model against measurements.

**Note on Simon et al. (1994):** we hoped to cite the classic Simon, Reddy and Kantak (1994) model through this paper, but this paper does not cite it. Simon et al. is behind a paywall; it stays on the list of papers to obtain.

**What it gives this project:**

| Point | What the paper says | Use for us |
| --- | --- | --- |
| Heat loss of a second incubator | Air-to-room thermal resistance 0.077 K/W on average (0.043 to 0.116 in three tests), room at 28 °C (Table 5) | 1 / 0.077 = about 13 W/°C (range 9 to 23 W/°C; our arithmetic). Close to our 14.8 W/°C from a different incubator, so our value is not an outlier |
| A validated model | Model temperatures within about 1.5 °C of measurements; largest errors during heating and cooling (Table 7) | An example of how our model should be validated |
| Switch-off behaviour | After switch-off "the computational model cools down more slowly than the experimental model"; the authors suspect the fan still running and air leaking from the incubator | A warning that a simple model can be optimistic about how slowly an incubator cools; our model may be too |
| Model structure | Air, mattress and heater nodes linked by resistances and capacities, solved with Runge-Kutta | The same family of model as ours |

**Measured cool-down data:** the switch-off test (37 °C setpoint, 28 °C room, 20 minutes of cooling, repeated three times) is shown only in a figure (Figure 6), not a table. The curve could be read off the figure later for a rough check of our cooling rate. It is not a blackout test: the room was warm, there was no baby, and the incubator had a thermoelectric heater.

**Limits to remember:** a different incubator, modified with a thermoelectric heater; the three resistance values differ by a factor of almost three, so the 13 W/°C figure is rough.

## 10. Delanaud et al. (2019)

**Citation:** Delanaud, S., Chahin Yassin, F., Durand, E., Tourneux, P., Libert, J.-P. (2019). Can mathematical models of body heat exchanges accurately predict thermal stress in premature neonates? *Applied Sciences*, 9(8), 1541. https://doi.org/10.3390/app9081541 (Open access.)

**Checked:** 2026-11-15, against the published PDF.

**What the paper is about:** a review of how a newborn in a closed incubator exchanges heat (convection, radiation, conduction, evaporation), and of the strengths and weak points of the models used to predict it.

**What it confirms for this project (baby-to-air heat transfer):**

| Baby's position (Wheldon's 3.3 kg manikin) | Convection hc (W/m²/°C) | Radiation hr (W/m²/°C) | Total (our arithmetic) |
| --- | --- | --- | --- |
| Foetal (curled) | 4.00 | 3.10 | 7.1 |
| Relaxed | 3.90 | 3.70 | 7.6 |
| Spread-eagle | 4.91 | 4.90 | 9.8 |

So our "7 to 9.8 W/m²/°C" is right (strictly 7.1 to 9.8). These numbers are second-hand: the original is Wheldon, A. E. (1982), *Physics in Medicine and Biology*, 27, 285-296, which we have not read.

**New points that matter for our model:**
- **Cold walls.** In single-walled incubators the walls the baby "sees" are cooler than the air: the mean radiant temperature is 4.0 to 5.5 °C below the air (Ultman et al.), 2.7 °C (Decima et al.), 3.1 °C (Wheldon) and 3.5 °C (Sinclair). Our model lets the baby exchange heat only with air at the air temperature, so it underestimates the baby's heat loss. This is the third source pointing to the same gap (see WHO 1997, entry 7, and Sauer et al. 1984, entry 4).
- **Smaller babies lose more.** Two manikins of 900 g and 1800 g: heat losses were 20.4 percent greater for the smaller one (Elabbassi et al., quoted here).
- **The manikin was large.** Wheldon's manikin simulated a 3.3 kg baby with a simple shape; the authors say measurements with manikins of premature babies are preferable.

**Possible model change (not made yet):** add a wall node, so the baby loses heat by convection to the air and by radiation to walls a few degrees cooler. This was idea #12 ("better baby and wall model") in our earlier list, and it now has published numbers to test it against.

**Limits to remember:** a review, so most numbers are quoted from other studies; we have checked them only as reported here.

## 11. Pfeifroth et al. (2024)

**Citation:** Pfeifroth, U., Drucke, J., Kothe, S., Trentmann, J., Schroder, M., Hollmann, R. (2024). SARAH-3 - satellite-based climate data records of surface solar radiation. *Earth System Science Data*, 16, 5243-5265. https://doi.org/10.5194/essd-16-5243-2024 (Open access.)

**Checked:** 2026-11-15, from the article text on the journal website (copied by hand) and screenshots of Tables 2 to 5.

**What the paper is about:** the SARAH-3 dataset of sunlight at the ground, estimated from Meteosat satellite images, and how well it matches ground measurements. PVGIS uses it as its default solar data for Africa.

**What it tells us about our solar data:**

| Point | What the paper says | What it means for us |
| --- | --- | --- |
| Area covered | 65° S to 65° N and 65° W to 65° E | Freetown, Bonthe, Kabala and Goma are inside. Dhaka (90° E) is outside, which explains why PVGIS used its other dataset (ERA5) for Dhaka |
| Detail | 0.05° grid (about 5 km), every 30 minutes | Fine enough for single towns |
| Accuracy of monthly sunlight | Mean bias about ±2 W/m²; mean absolute difference about 5 W/m² and RMSE 7 W/m² for monthly means at high-quality reference stations; daily values less accurate than monthly | Good on average |
| Tropical Africa | Errors in sunshine duration are "larger for the tropical and subtropical stations of Africa", where SARAH-3 mostly overestimates sunshine, by more than 30 hours a month at some stations | Our solar output for Sierra Leone and Goma may be slightly too high, so our panel and battery sizes may be slightly too small |
| Time periods | One consistent record for 1983 to 2020; from 2021 a near-real-time version with the same method; the paper advises care across that change | Our 2014 to 2023 data cross the change (2021) |

**Caution:** the overestimate in tropical Africa is reported for sunshine duration (hours of bright sun), not directly for the solar energy we use. It is a warning sign, not a measured error for our sites.

**Possible check later:** compare PVGIS's two datasets (SARAH-3 and ERA5) for Freetown, or ground measurements if any exist, to see how much our sizes change.

**Reference stations (Table 2, checked from a screenshot):** the 17 high-quality BSRN stations used to check SARAH-3 are mostly in Europe. The African ones are Tamanrasset (Algeria, 22.8° N, Sahara desert, 1,385 m), Gobabeb (Namibia, 23.6° S, desert) and De Aar (South Africa, 30.7° S); the others nearest the tropics are Reunion Island (20.9° S) and Solar Village (Saudi Arabia, 24.9° N). None is in humid tropical West or Central Africa. So the good accuracy figures (bias about ±2 W/m²) were not tested in a climate like Freetown's or Goma's.

**Other reference stations (Table 3):** the 23 GEBA stations used for monthly checks are all in Europe.

**Accuracy numbers (Table 4, BSRN stations; SIS = sunlight on a flat surface, which PVGIS builds on):**

| SIS accuracy | Monthly means | Daily means |
| --- | --- | --- |
| Bias | 2.1 W/m² | 2.0 W/m² |
| Mean absolute difference | 5.2 W/m² | 10.8 W/m² |
| RMSE | 7.0 W/m² | 15.9 W/m² |
| Anomaly correlation | 0.94 | 0.96 |

Direct sunlight (SID, DNI) is less accurate (daily RMSE 24.1 and 43.2 W/m²).

**Sunshine duration (Table 5, all CLIMAT and ECA&D stations):** bias 9.5 h and mean absolute difference 20 h for monthly sums; 0.2 h and 1 h for daily sums. The larger errors at African stations come from the map in the text (Figure 12), not from this table.

**Reading:** day-to-day errors are about twice the monthly ones. Our battery size is set by the worst run of cloudy days, so the daily accuracy is what matters for us, and it was measured mostly in Europe.

**Limits to remember:** no reference station in humid tropical Africa; all accuracy figures are averages over mostly European and desert stations.

## 12. McCord et al. (2026)

**Citation:** McCord, R., Miles, S. B., Mughuma, J. M., Kammen, D. M., Kwong, L. H. (2026). Assessing the impacts of sufficient and reliable electricity in low-resource healthcare facilities. *Proceedings of the National Academy of Sciences (PNAS)*, 123(38), e2538126123. https://doi.org/10.1073/pnas.2538126123

**Checked:** 2026-11-15, against the published PDF.

**What the paper is about:** whether reliable electricity changes patient outcomes. Surveys, power sensors and monthly health records from 303 facilities in three provinces of DR Congo (16,059 facility-months), analysed with methods designed to estimate cause and effect (targeted maximum likelihood estimation and two-way fixed effects).

**What it gives this project (the "why it matters" evidence):**

| Finding | What the paper says |
| --- | --- |
| Deaths among inpatients | Facilities with sufficient and reliable power (more than 22 hours of power a day) had a 41 percent lower inpatient mortality rate, 1.8 percentage points against an average of 4.5 percent in the other facilities |
| Keeping power reliable over time | In 18 facilities with sensors, months with more than 22 hours a day of power had mortality 1.8 percentage points lower |
| Children and newborns | Mortality fell in all wards, but significantly only in paediatric wards ("which includes neonatal mortality") and internal medicine |
| Other effects | 17 percent more outpatients and more days worked by nurses |

**How we will use it:** in the introduction, as the strongest evidence that unreliable power harms patients. The authors say their 22 hours a day threshold follows the WHO definition of reliable electricity (less than 2 hours of outage). The WHO survey definition is slightly different: no outage lasting more than two hours at a time in the previous one or two weeks (see entry 13).

**Limits to remember:** the main reliability measure comes from a one-time survey, while sensors show reliability changes a lot over time; the sensor analysis covers only 18 facilities; the effect is for whole facilities, not for incubators or newborns specifically; one country.

## 13. WHO, World Bank, IRENA and SEforALL (2023)

**Citation:** World Health Organization, World Bank, International Renewable Energy Agency, Sustainable Energy for All (2023). *Energizing Health: Accelerating Electricity Access in Health-Care Facilities.* Geneva: WHO. ISBN 978-92-4-006696-0. Free online. A report, not a peer-reviewed paper.

**Checked:** 2026-11-15, against the PDF (only the parts listed below).

**What it is:** the main global report on electricity in health facilities, based on national surveys from 27 low- and lower-middle-income countries (2015 to 2022).

**What it gives this project:**

| Point | What the report says |
| --- | --- |
| Scale of the problem | "close to 1 billion people in low- and lower-middle-income countries are served by health-care facilities without reliable electricity access or with no electricity access at all" |
| No electricity at all | About 12 percent of facilities in South Asia and 15 percent in sub-Saharan Africa |
| Reliable electricity | Only 40 percent of facilities in sub-Saharan Africa had reliable electricity; only half of hospitals there |
| Incubators need it | "Without an adequate and reliable source of power, some medical devices and services such as fetal heart monitors, incubators and ventilators cannot operate." |
| Critical loads | Baby warmers, oxygen concentrators and refrigerators are "critical loads" that must stay powered; lights and fans should not drain the power they need |
| Equipment failure | "Nearly a third of failures of medical devices globally was estimated to be caused by unreliable electricity supply" |
| Definition of reliable | A facility counts as reliable if it answers "no" to: "At any time in the previous one (or two) weeks, have you experienced an outage lasting more than two hours at a time?" |

**Second-hand items (cite the originals, not this report):** Apenteng et al. (2018) in Ghana, risk of death up 43 percent for each day the power was out for more than 2 hours; Duke et al. (2021), 40 percent lower paediatric mortality with reliable solar power and oxygen in Papua New Guinea.

**How we will use it:** the opening of the introduction (scale of the problem, incubators as critical equipment) and the definition of reliable electricity.

**Limits to remember:** survey-based (facilities report their own outages); the reliability question covers only one or two weeks; regional averages, not specific to neonatal units.
