# Parameter register and evidence log

This file is a chronological log. Later entries replace earlier ones. The current settings are in README.md and in model.py (class Params). Entries marked ASSUMPTION have no source yet.

Status key: ASSUMPTION = chosen by us, not yet validated. CHECKED = consistent with a source, but not measured.

| Parameter | Value | Status | Basis |
|---|---|---|---|
| Heater rating | 300 W | CHECKED | 200 W fails the VNG 3000 warm-up spec (22 to 35 °C in under 20 min); 300 W gives 16 min in our model |
| Heat loss UA | 5 W/°C (range 3 to 8) | CHECKED | Nwaneri et al. 2020 (WIJE 43(1)): Table 5 gives about 4.2 W/°C (some areas missing, likely low); Fig 14 slope about 5.4 W/°C (read by eye) |
| Incubator thermal capacity | 20000 J/°C (5000 to 30000 tested) | ASSUMPTION | No source for a neonatal incubator; Kapen et al. 2019 suggests about 5000 or more for a small rig. Does not change battery sizing |
| Room temperature | 22 °C | ASSUMPTION | VNG 3000 sheet gives operating range 20 to 30 °C |
| Air setpoint | 33.5 °C | CHECKED | Hospital guideline gives 33.5 °C for a 2000 g baby in the first 3 days; a handbook chart gives 31 to 34 °C (changed from 34 °C) |
| Baby mass | 2 kg | ASSUMPTION | Illustrative preterm baby |
| Baby tissue specific heat | 3500 J/kg/°C | ASSUMPTION | Not yet sourced |
| Baby heat loss to air (hA) | 0.86 W/°C (= metabolic heat / 3.5) | ASSUMPTION | Set so the baby balances at 37.0 °C in 33.5 °C air. Delanaud et al. 2019 quotes 7 to 9.8 W/m2/°C for a 3.3 kg mannequin, but the skin area of a 2 kg baby is not sourced |
| Baby metabolic heat | 3 W (2 to 4 W tested) | ASSUMPTION | Not given in Delanaud et al. 2019; range not sourced |
| Converter efficiency | 0.9 | ASSUMPTION | Typical value, not sourced |
| Usable battery fraction | 0.8 | ASSUMPTION | Design choice |

## Sources reviewed and not used
- AI-generated search summaries on incubator power: figures disagree by about 4 times, no room temperature stated.
- Debekeme et al. (solar biomedical incubator): laboratory incubator at 37 °C, not neonatal; its 1.10 kWh/day is an estimate that does not match its own 5.2 W heat loss calculation.
- Kalstein YR02186, VNG 3000 and tender specification: give maximum power (450 to 650 VA) only, not steady-state power.

## Delanaud et al. 2019 (Appl. Sci. 9(8), 1541, doi 10.3390/app9081541)
- Review paper. Gives heat balance structure: S = M +/- R - E - Eresp +/- C +/- Cresp +/- K. Our baby model is a single lumped term, a simplification.
- Optimal core temperature 36.5 to 37.5 °C. WHO cold stress described as core 36.0 to 32.0 °C. Our README labels (moderate/severe hypothermia) come from memory and must be checked against WHO 1997 "Thermal Protection of the Newborn".
- Mean radiant temperature in single-wall incubators reported 2.7 to 5.5 °C below air temperature. Our model ignores radiant exchange with the walls, so it probably under-estimates cooling in a blackout (LIMITATION).
- Wheldon (3.3 kg mannequin, via Delanaud): hc 3.9 to 4.9, hr 3.1 to 4.9 W/m2/°C. Total 7 to 9.8 W/m2/°C. Needs skin area of a 2 kg preterm baby to convert to hA (not yet sourced).
- Metabolic heat: not given in this paper. A later Delanaud paper (Appl. Sci. 2023, 13(7), 4412) mentions 2.70 W/kg in one scenario, not yet read. Our 3 W for 2 kg (1.5 W/kg) may be low.
- M and hA must be calibrated together: core temperature at balance = air temperature + M / hA.

## calibrated baby model (current settings)
- Air setpoint changed from 34 °C to 33.5 °C. Basis: hospital guideline value for a 2000 g baby in the first 3 days (CHECKED, single guideline); handbook chart (Merenstein and Gardner 2006, via RCH) gives 32.8 to 33.8 °C for 1501 to 2500 g in the first 6 h.
- Baby starting core temperature 37.0 °C. Basis: midpoint of the neutral-temperature core range 36.7 to 37.3 °C (Saur et al. 1984).
- Metabolic heat M: 2 to 4 W tested (ASSUMPTION, range not yet sourced). hA calibrated as M / (37.0 - 33.5), giving 0.57 to 1.14 W/°C.
- Results: no battery, 2 h blackout: lowest core 32.0 to 33.9 °C. Smart rule: about 37.0 °C. Battery energy about 129 Wh (about 161 Wh rated at 80 percent usable).

## controller and room temperature
- Controller: feedback rule, battery on below setpoint minus 0.8 °C, off above setpoint minus 0.3 °C (ASSUMPTION, chosen values).
- Room temperature: 22 °C baseline (ASSUMPTION). Datasheets list an operating environment of 20 to 30 °C, so 16 °C is outside rated conditions and is used only as a stress case.
- Outage scenario: 60 min at 50% voltage then 120 min blackout (ASSUMPTION, no source yet).
- Results: feedback rule rating 120 to 489 Wh across room 16 to 22 °C and UA 4 to 8 W/°C; lowest core 36.59 to 36.70 °C.


- Correction: an earlier script counted battery energy while the grid was normal, over-counting by up to about 90 Wh for a 0.4 °C trigger and about 2 Wh at 0.8 °C. Fixed before the model was consolidated into model.py. Baby temperatures were unaffected.

## outage evidence and other sources reviewed
- Miles et al. 2025 (Applied Energy 401, 126830), 25 facilities North Kivu DRC, sensors, 29 months: 0.67 outages/day on average (max about 2); median outage duration averaged 2.01 h (0.03 to 10.9 h); by type HGR 1.17 h, CSR 3.80 h, CS 3.91 h, private hospitals about 0.16 h; mean uptime 93.2%; voltage within +/-10% of 230 V about 74% of the time. Duration is probably per outage (uptime formula multiplies count by duration) but the paper labels it hours/day: CHECK supplementary data.
- Sag depth and duration are not reported. Data available on request from the authors.
- Franco et al. 2017: incubator 420 W x 24 h = 10,080 Wh/day is rating x hours, an upper bound, not a measurement. Battery charge ideally kept at 20 to 80 percent. Usable fraction 0.8 fits Li-ion and NiMH; lead-acid would be lower (Debekeme et al. used 60 percent depth of discharge).
- Not used: Franco claim that up to 70 percent of breakdowns come from end-of-outage surges (Miles et al. describe the same source, Malkin 2007, as not identifying the cause). nLine blog figures (unit errors, monthly totals). Apenteng 43 percent mortality figure (second-hand, original not read).
- Irwin et al. 2020: abstract only; evidence quality on reliability and health outcomes described as weak.
- Model gaps: fan and electronics load not included (value unknown, needs a source); repeated outages and recharge not modelled; battery capacity not limited in simulation.

## Messersmith et al. 2022 (Gates Open Res 6:58, doi 10.12688/gatesopenres.13479.1)
- Qualitative study: 9 hospitals in Maharashtra, India, 66 participants (35 key informants, 31 focus group), Dec 2019 to Nov 2020. No measured outage durations or voltages.
- Main finding: staff and engineers attribute equipment failure (including radiant warmers) to sags, surges and spikes; they recommend online UPS, stabilizers and power audits.
- All 9 facilities had working generators; one nurse said the generator takes over within a minute (single self-reported quote).
- Warmers trip circuits in winter when all are in use.
- UNICEF SNCU toolkit (via the paper, original not read): 24 h uninterrupted stabilised supply, backup supply and generator for each piece of equipment.
- Implication: damage to the incubator from surges and sags is not modelled. Our outage scenario is most relevant where backup is slow, absent or fuel-limited.
- Sierra Leone: CORRECTED after reading Wall et al. 2024. The claim of 3 outages per day with median 3 h each is not in the report; 3.07 per day is the single worst facility.


## Papers reviewed: Sierra Leone sensor data, thermal models and power-quality papers
- Wall et al. 2024 (IGC report SLE-20186, nLine): 15 public facilities in Sierra Leone, 6 weeks (20 Jul to 31 Aug 2023), outlet sensors. Outages per day 0.63 to 3.07. Average daily hours without power 0.03 to 18.43 (hospitals 5.83, CHCs 4.37). Executive summary says up to 9 h per day, which conflicts with 18.43 in the body (CHECK). No average length per outage is reported; hours per day divided by outages per day gives about 1 to 2 h at Wellington CHC (our arithmetic).
- Voltage (nominal 230 V, band 207 to 253 V): hospitals average 227 V, CHCs 206 V, CHC average minimum 170 V. Lowest recorded 127 V (0.55 pu) at Wellington CHC, which spent 12.78 h per day outside the band. East Freetown average 192 V. Hastings CHC grid power averaged 139 to 195 V (0.60 to 0.85 pu) against 215 V from solar.
- Waterloo CHC had no power from 28 July to at least 31 August 2023 (unpaid grid bills, no generator fuel). Out of scope for a battery.
- Kapen et al. 2019 (Health Technol 9:57-63): single-wall 5 mm plexiglass box 1020 x 675 x 400 mm, 100 W heater, 37 °C in about 15 min. Printed heat balance 309.66 dT/dt = 1231.59 - 3.795 T (T in K) implies a calculated loss coefficient of 3.8 W/K, supporting UA of 3 to 5 (calculated, not measured). Its 309.66 J/K capacity looks like air only and would give about 1 min warm-up, not 15 (could not reproduce their fit): do not use their capacity. A 15 min warm-up at 100 W suggests an effective capacity of roughly 5 kJ/K or more; our 20 kJ/K may be high (TEST).
- Feles et al. (Instruments 9, 21; DLR transport incubator, not neonatal): measured heating power vs ambient across 21 conditions (0 to 15 °C) at 37 °C: q = -1.9837 x Tamb + 73.398 W (loss about 2 W/K). Electronics baseline 17.3 W (SD 2.0) measured separately. Numbers not transferable; the method is what we need. Model worst case deviated up to 40 percent from measurements.
- Murkovic et al. 2003: thermistors accurate to about 0.5 °C, thermocouples about 0.1 °C; skin thermistor tracks rectal core temperature well in stable convective incubators. Our 0.2 to 0.8 °C margins are at or below typical sensor accuracy.
- Idris and Azeez 2026 (IJAMRED 2(3)): quotes IEEE 1159 sag definition, 0.1 to 0.9 pu for 0.5 cycle to 1 min. A 60 min event at 0.5 pu is a sustained undervoltage, not a sag. Quoted regulator ranges: relay +/-15 to 25 percent, servo +/-20 to 30 percent, so a regulator cannot restore 0.5 to 0.6 pu. Its field results (58 to 81 percent failure reduction, USD 1.2 million savings) are not verified and not used.
- Not used: JOBASR 2026 STATCOM simulation (0.5 pu sag lasting 0.1 s, wrong timescale); Osunmuyiwa et al. 2025 (household power quality in Accra); Kerbala 2020 bachelor project (laboratory incubator, 1500 W heater).

## Sustained undervoltage and thermal capacity
- Sustained undervoltage, 6 h, room 22 °C, setpoint 33.5 °C, feedback trigger 0.6 °C: a 300 W heater needed 0 Wh at every grid voltage from 0.55 to 0.85 pu for UA 5 and 8 (lowest core 36.84 °C at UA 8 and 0.55 pu). A 200 W heater needed 0 Wh at UA 5; at UA 8 it needed 180 Wh at 0.6 pu and 275 Wh at 0.55 pu (core 36.67 °C). Assumes a fixed-resistance heater (power proportional to V squared), constant voltage, and that the fan and controller still run at 0.55 pu (127 V). That is doubtful: Sierra Leone staff reported grid power too low to run a fan.
- Trigger 0.6 °C chosen because the thermostat swings +/-0.5 °C; a 0.4 °C trigger lies inside the swing and would engage the battery on normal cycles.
- Thermal capacity test (2 h blackout, 300 W, UA 5, room 22 °C): feedback battery energy 120 to 126 Wh and lowest core 36.79 to 36.80 °C for C = 5, 10, 20, 30 kJ/°C. No battery: lowest air 22.0, 22.3, 24.0, 25.4 °C and lowest core 30.9, 31.7, 33.0, 33.6 °C. Capacity does not change battery sizing; it changes how fast an unprotected incubator cools. The 1 to 6 min until trigger probably reflects the thermostat phase when the blackout starts (not tested).

## Repeated outages
Settings: UA 5, room 22 °C, 300 W heater, immediate transfer to battery on mains failure, 60 W charger (ASSUMPTION), 48 h, 3 outages per day.
- 1.5 h outages: each outage uses about 100 Wh. Rating 150 Wh and above never empties (lowest core 36.99 °C); 100 Wh is empty for 87 min in total (lowest core 36.82 °C).
- 3 h outages: each outage uses about 192 Wh. Rating 300 and 400 Wh never empty (36.99 °C); 200 Wh empty about 33 min per outage (36.40 °C); 150 Wh (35.10 °C); 100 Wh (33.33 °C).
- Battery returned to full between outages in every case (gaps of 5 to 6.5 h). Not tested: clustered outages, battery ageing, charger rating, grid undervoltage during recharge.

## Reproduction check (reproduce_findings.py)
- 46 of 48 README claims reproduced by model.py. Blackout energy corrected from 65 to 67 Wh per hour to about 64 Wh per hour (63.9 = UA x temperature difference / efficiency); short events vary because of thermostat timing (not tested). The 8 h and 11 h figures are now simulated (507 and 699 Wh used).


## Published support for assumed inputs (research round 2)
Status: CITED = a published value supports it; DERIVED = our arithmetic from published values; ASSUMPTION = no source. Authors and full details to be confirmed from the PDFs before any write-up.
- Baby heat production: oxygen consumption 5.8 +/- 0.8 mL/kg/min in thermoneutral incubators, preterm infants under 1500 g (J Pediatr 1997, skin-to-skin study; authors to confirm) = about 1.9 W/kg (DERIVED at 20.1 J per mL O2). Resting energy expenditure 57.0 +/- 7.8 kcal/kg/day in 29 very low birth weight infants, mean 1.56 kg, indirect calorimetry (paper hosted on Redalyc; details to confirm) = about 2.8 W/kg (DERIVED). A patent summary of an older paper gives 1.75 to 4.37 kcal/kg/h = 2.0 to 5.1 W/kg (secondhand). Our earlier 3 W for 2 kg (1.5 W/kg) was below this range. New default 2.0 W/kg.
- Baby surface area: Boyd weight-only table (Sharkey et al., Br J Cancer 2001; 85:23-28): 2 kg 0.16 m2, 3 kg 0.21, 4 kg 0.26. Measured about 0.100 m2 at 1.06 kg (Korycki and Krucinska, 2013 conference paper). Haycock 1978 (J Pediatr 93:62-66) is validated from premature infants to adults. Our scaling A = 0.16 x (W/2)^0.67 gives 0.105 m2 at 1.06 kg and 0.254 m2 at 4 kg (DERIVED).
- Baby heat transfer: 7 to 9.8 W/m2/°C total (Wheldon, 3.3 kg manikin, quoted in Delanaud et al. 2019). Times the area gives hA of 1.1 to 1.6 W/°C at 2 kg, 0.70 to 0.98 at 1 kg, 1.8 to 2.5 at 4 kg. The value from neutral balance (2.0 W/kg x mass / (37.0 - neutral air temperature)) is 1.14, 0.95 and 1.82 W/°C, inside or at the edge of each range (DERIVED).
- Radiant share: 68 +/- 3 percent of total heat loss in 16 babies under 1500 g in a convective incubator (Pediatr Res 1984). Cold walls therefore matter; the model does not include them.
- Air setpoint by weight (CITED): UCSF Benioff manual 2004, first 24 h: 500 g 35.5, 1000 g 34.9, 1500 g 34.0, 2000 g 33.5, 2500 g 33.2, 3000 g 33.0, 3500 g 32.8, 4000 g 32.6 °C. NHS Worcestershire guideline, first 3 days: 1000 g 35, 1500 g 34, 2000 g 33.5, 2500 g 33.2, 3000 g 33, 4000 g 32.5 °C. The same guideline says babies under 1000 g may occasionally need more than 37 °C.
- Baby specific heat: tissue values 3020 to 3770 J/kg/°C (1996 premature-infant model, WIT Press, Table 2). 3500 is inside (CITED, range).
- Heater power: 100 to 300 W typical (hospital workshop reference); 420 W rated (Franco et al. 2017); VNG warm-up spec fits about 300 W. CONSISTENT.
- Heat loss UA: calculated 3.8 (Kapen 2019) and 4.2 (Nwaneri 2020) W/°C. Measured about 1.9 W/°C for a small low-cost incubator (30 W at 37.5 °C in a 22 °C room; ScienceDirect technology brief, 2022) and about 2 W/°C for the DLR transport incubator: both much smaller than a neonatal hood. A commercial resistance incubator was measured at 36 °C hood and 25 °C room by Koseoglu (Eng Sci Technol Int J, 2021) and Yeler and Koseoglu (J Electron Mater 49:4053, 2020); both paywalled, to be read. Still ASSUMPTION (plausible).
- Fan and electronics load: an Applied Thermal Engineering 2020 abstract (modular thermoelectric heat pump premature baby incubator) says about 80 to 90 percent of total electrical power in a resistance incubator goes to the heater, leaving 10 to 20 percent: roughly 6 to 14 W when the heater averages 57 W (DERIVED). DLR lab incubator electronics 17.3 W. Context to confirm from the full text.
- Thermal capacity: no published neonatal value found; the Kapen warm-up timing suggests about 5 kJ/°C or more for a small rig. ASSUMPTION; it does not change battery size.
- Battery usable share: Franco et al. 2017 (lithium, nickel and sodium batteries: 80 percent depth of discharge; charge state ideally 20 to 80 percent). Victron LiFePO4 datasheet: 2500 cycles at 80 percent depth, 5000 at 50 percent. CITED, with a life trade-off.
- Converter efficiency: Victron MultiPlus-II 48/3000 maximum efficiency 95 percent, zero-load draw 11 W (retailer-listed specification); LiFePO4 round trip 92 percent (Victron). At a 60 W load the idle draw alone cuts efficiency to about 85 percent (DERIVED). 0.9 is slightly optimistic; a DC-powered heater avoids the inverter.
- Prior art found: thermal models of incubator and baby (Delanaud et al. review; Simulink model of a Drager incubator; Auckland University of Technology thesis; optimal-control and multi-node models) and battery or solar prototypes (Bangladesh suggestion; Cameroon 16 h claim; Indonesia 22 to 32 h test). Not found, in a limited search: a study coupling baby response, measured outage data and battery sizing. Write "not found in my search", not "does not exist".
