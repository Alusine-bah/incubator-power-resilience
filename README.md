# Resilient Infant Incubator: Power Failure Simulation

**Try it online:** [live dashboard](https://incubator-power-resilience.streamlit.app) | **More projects:** [portfolio](https://alusine-bah.github.io)

## Summary
When the grid fails, how long does a baby in an incubator stay warm, and how big must a backup battery be? This project simulates an incubator, a preterm baby (0.5 to 4 kg) and a backup battery through blackouts and long low-voltage events. It uses a heat loss measured on one commercial incubator and outage data from published sensor studies, and a script re-runs every number in this README against the model.

Main results for the default incubator, a 2 kg baby and a 22 °C room. Inputs that are assumptions are listed in PARAMETERS.md.
- With no backup, a 2 h blackout lowers the modelled core temperature of a 2 kg baby to about 30 °C. Across birth weights it falls to about 25 °C (0.5 kg) to 31 °C (4 kg). Below about 30 °C the model has no physiology, so read these as severe cold exposure and not as precise predictions.
- With a battery that takes over at once, the baby stays at about 37 °C. The battery supplies about 190 Wh per outage hour, so a rated battery of about 237 Wh per outage hour at 80 percent usable: 475 Wh for 2 h, 712 Wh for 3 h, 1,895 Wh for 8 h and 2,607 Wh for 11 h.
- Smaller babies need more battery for the same blackout, because their warmer air setpoint widens the gap to the room: 561 Wh at 0.5 kg against 436 Wh at 4 kg for 2 h.
- Heat loss is the main lever. For a 2 h blackout the rated battery is 158 Wh at 5 W/°C, 256 Wh at 8, 350 Wh at 11, 475 Wh at 14.8 (measured) and 642 Wh at 20. A lower heat loss shrinks the battery in proportion; whether a practical incubator can reach a low value was not tested.
- Low voltage: the 350 W heater holds the setpoint with no battery when the grid is at 0.7 of nominal or higher. At 0.6 for 6 h the rated battery must be about 508 Wh, and at 0.55 about 706 Wh. Without backup the baby spends 506 minutes (0.6) and 553 minutes (0.55) below 36.5 °C. Sensors in Sierra Leone recorded grid voltage as low as 0.55 of nominal.
- Charger: for three 2 h blackouts a day, a 476 Wh battery works if the charger delivers 100 W or more. With a 60 W charger the battery cannot refill between blackouts and 814 Wh is needed. For 3 h blackouts the figures are 713 Wh with a 200 W charger and 2,566 Wh with 60 W.
- Not validated: the heat loss comes from one device, and several other inputs rest on a single source or are assumptions (see the table below and PARAMETERS.md).

![Baby temperature in a 2 h blackout, with and without a 500 Wh battery](docs/blackout_example.png)

**Educational model. Not a medical device and not for clinical decisions.**

## Files
- model.py: the simulation and all parameters
- app.py: interactive dashboard
- check_model.py: tests the model against earlier results and published ranges
- reproduce_findings.py: re-runs every number in this README through the model
- make_figure.py: regenerates the example figure in docs/
- PARAMETERS.md: where each input comes from, the papers reviewed, and open issues

## How to run
- Install the packages: python -m pip install -r requirements.txt
- Check the model: python check_model.py
- Check every README number against the model: python reproduce_findings.py
- Start the interactive dashboard: python -m streamlit run app.py
- Regenerate the example figure: python make_figure.py

## Model (default settings)
| Input | Value | Source or status |
|---|---|---|
| Heat loss, incubator to room | 14.8 W/°C | Measured on one commercial incubator (built 2006, empty hood): 162.95 W at 36 °C inside and 25 °C outside (Yeler and Koseoglu 2020, 2022). Earlier calculated values of 3.8 and 4.2 W/°C (Kapen 2019, Nwaneri 2020) were for simple prototypes |
| Heater | 350 W | Close to the 368 W maximum measured on that incubator; the model warms from 22 to 35 °C in about 18 min |
| Air setpoint | 35.5 °C (0.5 kg) to 32.6 °C (4 kg) | Hospital manual table for the first 24 hours (UCSF 2004); a UK guideline agrees within 0.1 °C |
| Baby heat production | 2 W per kg | Preterm oxygen consumption (about 1.9 W/kg) and resting energy expenditure (about 2.8 W/kg); two citations still to confirm, see PARAMETERS.md |
| Baby heat loss | Set so the baby balances at 37 °C at its setpoint | Consistent with published coefficients (7 to 9.8 W/m2/°C) times body surface area (derived) |
| Baby specific heat | 3,500 J/kg/°C | Inside published tissue values (3,020 to 3,770) |
| Heat stored in the incubator | 20 kJ/°C | Assumption; does not change battery size |
| Room temperature | 22 °C | Datasheets list 20 to 30 °C |
| Battery usable share | 80 percent | Cited for lithium batteries (Franco et al. 2017), at a cost in battery life |
| Converter efficiency | 90 percent | Slightly optimistic at small loads (inverter idle draw) |
| Charger | 200 W | Assumption; it must be able to refill the battery between outages |

## Controller
- Mains failure: switch to the battery at once. A real device can detect this directly (a commercial datasheet lists a power-failure alarm within 30 s).
- Partial undervoltage: use the battery when the air falls 0.6 °C below setpoint, hand back at 0.1 °C below setpoint. The trigger must sit below the thermostat swing of +/-0.5 °C; a trigger of 0.8 °C let the baby settle just below 36.5 °C in long events.
- Sensor accuracy (thermistor about 0.5 °C) is comparable to these margins.

## Evidence for the scenarios
- Sierra Leone, 15 public health facilities, 6 weeks of outlet sensors: 0.6 to 3.1 outages a day, 0.03 to 18 hours a day without power, grid voltage down to 127 V (0.55 of 230 V) (Wall et al. 2024).
- North Kivu, DR Congo, 25 facilities, 29 months: the median outage averaged 2.0 hours, ranging from 0.03 to 10.9 hours (Miles et al. 2025).
- Nine special neonatal care units in India: staff blamed voltage sags and surges for equipment damage (Messersmith et al. 2022). This model does not cover that.
- Some facilities are without power for weeks because they cannot pay for grid power or fuel. A battery cannot fix that.

## Limitations
- The heat loss is measured on one device, at one operating point, with an empty hood. Other incubators will differ, and the battery size scales directly with it.
- No heat exchange with cooling walls (about two thirds of a small baby's heat loss is radiant), which likely makes the baby cool too slowly in the model. The baby's own response to cold is left out, which likely makes it cool too fast. The net effect is unknown.
- Evaporative heat loss and humidity are not modelled, and they matter a lot for babies under about 1 kg. The setpoints are for the first day of life; older babies need cooler air.
- The fan stopping in a blackout, the fan and electronics load, battery ageing, short sags and surges, and clustered outages are not modelled. The heater is a fixed resistance and the fan and controller are assumed to keep running at low voltage.
- Outage patterns are chosen from published ranges, not from one dataset. The outage and heat-loss inputs have not yet been varied together to show how sure the conclusions are.
- Temperature classes (WHO: moderate hypothermia 32.0 to 35.9 °C, severe below 32.0 °C) are measured under the arm; the model gives core temperature, so comparisons are approximate.

## How the numbers changed
The first version assumed a heat loss of 5 W/°C, which gave a rated battery of about 158 Wh for a 2 h blackout and a no-backup baby temperature of about 31 to 34 °C. A published measurement on a commercial incubator gives about three times that heat loss, which triples the battery sizes above. Those earlier figures were superseded and are kept only as the legacy test case in check_model.py.

## Next steps
- Vary the heat loss, baby heat production and outage inputs across their published ranges and report how often each battery size protects the baby.
- Find a measurement on a second incubator, and a measured fan and electronics load.
- Test clustered outages and a second dataset of outage lengths.

## Author
Alusine Bah

## License
MIT. See the LICENSE file.
