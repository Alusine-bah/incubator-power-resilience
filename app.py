import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from model import Params, grid_profile, repeated_outages, simulate, setpoint_for_weight

D = "\u00b0C"

st.set_page_config(page_title="Incubator power-failure simulator", layout="wide")
st.title("Infant incubator: what happens to the baby when the power fails?")
st.caption(
    "A simple educational simulation of an incubator, a preterm baby and a backup battery. "
    "Most inputs are assumptions or come from a single source (see the table at the bottom). "
    "This is not a medical device and must not be used for clinical decisions."
)
st.info(
    "The default heat loss (14.8 W per " + D + ") was measured on one commercial incubator (built 2006, empty hood, "
    "36 " + D + " inside, 25 " + D + " room). Other incubators will differ, so use the heat-loss slider to explore."
)

sb = st.sidebar
sb.header("1. The incubator")
heater = sb.slider("Heater power (W)", 150, 500, 350, 25,
    help="Heater power at full voltage. 350 W is close to the 368 W maximum measured on a commercial incubator. With the defaults the model warms the incubator from 22 to 35 degrees in about 18 minutes.")
ua = sb.slider("Heat leaking to the room (W per " + D + ")", 2.0, 20.0, 14.8, 0.1,
    help="Watts lost for every degree the incubator is warmer than the room, including the warm air that leaves through ventilation. 14.8 is measured on one commercial incubator. Earlier calculated values (3.8 and 4.2) were for simple prototypes. Battery size scales directly with this number.")
room = sb.slider("Room temperature (" + D + ")", 16, 30, 22,
    help="Datasheets list 20 to 30 degrees. Below 20 is a stress test.")
cap = sb.slider("Heat stored in the incubator (kJ per " + D + ")", 5, 30, 20,
    help="Assumption. It does not change the battery size, but it changes how fast an unprotected incubator cools.")

sb.header("2. The baby")
weight = sb.slider("Birth weight (kg)", 0.5, 4.0, 2.0, 0.1,
    help="Sets the incubator air temperature from a published table for the first day of life (500 g: 35.5 degrees, 2 kg: 33.5, 4 kg: 32.6), the baby's heat production, heat loss and heat capacity.")
sb.caption("Air setpoint for this weight: " + f"{setpoint_for_weight(weight):.1f} " + D)
meta = sb.slider("Baby's heat production (W per kg)", 1.5, 3.0, 2.0, 0.1,
    help="From oxygen consumption of preterm babies (about 1.9 W per kg) and resting energy expenditure (about 2.8 W per kg). The baby's heat loss is set so the baby balances at 37.0 degrees at its air setpoint.")

sb.header("3. The backup battery")
rating = sb.slider("Battery size (Wh)", 0, 2000, 500, 25,
    help="Rated capacity. Only 80 percent is treated as usable and the converter is 90 percent efficient (both assumptions).")
trigger = sb.slider("Low-voltage trigger (" + D + " below setpoint)", 0.2, 1.0, 0.6, 0.1,
    help="During low voltage (not a full blackout) the battery takes over when the incubator air falls this far below its setpoint. Keep it above 0.5, because the thermostat normally swings 0.5 either side of the setpoint.")
charger = sb.slider("Charger power (W)", 20, 500, 200, 10,
    help="Assumption. The charger must be strong enough to refill the battery between outages: with a weak charger, repeated blackouts drain the battery a little more each time.")

sb.header("4. What goes wrong")
scenario = sb.radio("Type of event",
    ["One blackout", "Long low voltage (brownout)", "Repeated blackouts (3 a day for 2 days)"])
if scenario == "Long low voltage (brownout)":
    length = sb.slider("How long the voltage stays low (hours)", 0.5, 11.0, 6.0, 0.5)
    vfrac = sb.slider("Grid voltage (fraction of normal)", 0.4, 0.95, 0.6, 0.05,
        help="Sensors in Sierra Leone recorded grid voltage as low as 0.55 of normal, and averages of 0.60 to 0.85 at some facilities.")
else:
    length = sb.slider("How long each blackout lasts (hours)", 0.5, 11.0, 2.0, 0.5)
    vfrac = 0.0


@st.cache_data
def run_case(heater, ua, room, cap, weight, meta, trigger, charger, scenario, length, vfrac, rating):
    p = Params(heater_w=float(heater), ua=float(ua), room_c=float(room),
               air_capacity=cap * 1000.0, baby_mass_kg=float(weight),
               metabolic_w_per_kg=float(meta), trigger_drop_c=float(trigger),
               charger_w=float(charger))
    if scenario == "Repeated blackouts (3 a day for 2 days)":
        events = repeated_outages(length)
        hours = 48
    elif scenario == "One blackout":
        events = [(0.5, length, 0.0)]
        hours = 0.5 + length + 4
    else:
        events = [(0.5, length, vfrac)]
        hours = 0.5 + length + 4
    grid = grid_profile(events, hours)
    big = 1000000.0
    unlimited = simulate(p, grid, big)
    needed = (p.usable_fraction * big - unlimited["lowest_charge_wh"]) / p.usable_fraction
    return grid, simulate(p, grid, rating), simulate(p, grid, 0), needed, p.setpoint_c


grid, with_b, without, needed, setpoint = run_case(
    heater, ua, room, cap, weight, meta, trigger, charger, scenario, length, vfrac, rating)

a1, a2, a3 = st.columns(3)
a1.metric("Lowest baby temperature, with backup", f"{with_b['lowest_core']:.2f} {D}")
a2.metric("Lowest baby temperature, no backup", f"{without['lowest_core']:.2f} {D}")
a3.metric("Minutes below 36.5 " + D + ", with backup", f"{with_b['minutes_core_below_36_5']:.0f}")
b1, b2, b3 = st.columns(3)
b1.metric("Battery energy used", f"{with_b['battery_used_wh']:.0f} Wh")
b2.metric("Battery size this event needs", f"{needed:.0f} Wh",
          help="Smallest rated battery that never runs empty in this scenario (80 percent usable), allowing for the charger refilling it between outages. With a weak charger this can be much larger than the size for one blackout.")
b3.metric("Minutes the battery was empty", f"{with_b['minutes_battery_empty']:.0f}")

if with_b["minutes_battery_empty"] > 0:
    st.error("The battery ran out during a blackout, so the baby lost its heating.")
elif with_b["lowest_core"] < 36.5:
    st.warning("The baby's modelled temperature fell below 36.5 " + D + ".")
else:
    st.success("With this backup, the baby's modelled temperature stayed at or above 36.5 " + D + ".")
if min(with_b["lowest_core"], without["lowest_core"]) < 30.0:
    st.caption(
        "Below about 30 " + D + " the model has no physiology to rely on. Read those values only as "
        "'severe cold exposure', not as precise predictions."
    )

st.caption(
    "Normal core temperature is 36.5 to 37.5 " + D + ". Moderate hypothermia is 32.0 to 35.9 " + D +
    " and severe is below 32.0 " + D + " (WHO classes, measured under the arm; this model gives core "
    "temperature, so the comparison is approximate)."
)

step = 30
t = np.arange(len(grid))[::step] / 3600.0
fig, ax = plt.subplots(4, 1, sharex=True, figsize=(10, 10))
ax[0].plot(t, grid[::step] * 230.0)
ax[0].set_ylabel("Grid voltage (V)")
ax[1].plot(t, with_b["air"][::step], label="with backup")
ax[1].plot(t, without["air"][::step], "--", label="no backup")
ax[1].axhline(setpoint, color="gray", ls=":")
ax[1].set_ylabel("Air in incubator (" + D + ")")
ax[1].legend()
ax[2].plot(t, with_b["core"][::step], color="tab:red", label="with backup")
ax[2].plot(t, without["core"][::step], "--", color="tab:orange", label="no backup")
ax[2].axhline(36.5, color="gray", ls=":")
ax[2].set_ylabel("Baby (" + D + ")")
ax[2].legend()
ax[3].plot(t, with_b["charge"][::step], color="tab:green")
ax[3].set_ylabel("Battery charge (Wh)")
ax[3].set_xlabel("Time (hours)")
fig.tight_layout()
st.pyplot(fig)

with st.expander("Where the scenarios come from"):
    st.write(
        "Sierra Leone, 15 public health facilities, 6 weeks of sensor data: 0.6 to 3.1 outages a day, "
        "0.03 to 18 hours a day without power, grid voltage down to 127 V (0.55 of 230 V) (Wall et al. 2024). "
        "North Kivu, DR Congo, 25 facilities, 29 months: the median outage averaged 2.0 hours, ranging from "
        "0.03 to 10.9 hours (Miles et al. 2025). "
        "Nine special neonatal care units in India: staff blamed sags and surges for equipment damage, "
        "which this model does not cover (Messersmith et al. 2022). "
        "Some facilities are without power for weeks because they cannot pay for grid power or fuel. "
        "A battery cannot fix that."
    )

with st.expander("What this model leaves out"):
    st.write(
        "Heat exchange with the cooling walls (about two thirds of a small baby's heat loss is radiant), which probably "
        "makes the baby cool too slowly in the model. The baby's own response to cold, which probably makes it cool too fast. "
        "The two effects pull in opposite directions and the net effect is unknown. "
        "Evaporative heat loss and humidity, which matter a lot for babies under about 1 kg. "
        "The air setpoints are for the first day of life; older babies need cooler air. "
        "The fan stopping in a blackout (the incubator then loses less heat to ventilation, but the air stops mixing). "
        "Also left out: the fan and electronics load, battery ageing, short sags and surges, and clustered outages. "
        "The heater is a fixed resistance, and the fan and controller are assumed to keep running at low voltage."
    )

with st.expander("Which inputs have a source?"):
    st.table([
        {"Input": "Heat leaking to the room (14.8)", "Status": "Measured on one commercial incubator (162.95 W at 36 degrees inside, 25 outside; Yeler and Koseoglu 2020, 2022). Other incubators will differ"},
        {"Input": "Heater power (350 W)", "Status": "Close to the 368 W maximum measured on that incubator"},
        {"Input": "Air setpoint by weight", "Status": "Hospital manual, first 24 hours (UCSF 2004); a UK guideline agrees within 0.1 degrees"},
        {"Input": "Baby heat production (2 W per kg)", "Status": "Published oxygen consumption (about 1.9 W per kg) and energy expenditure (about 2.8 W per kg) of preterm babies"},
        {"Input": "Baby heat loss", "Status": "Set so the baby balances at 37 degrees; consistent with published coefficients times body surface area"},
        {"Input": "Baby specific heat (3.5 kJ per kg per degree)", "Status": "Inside published tissue values (3.0 to 3.8)"},
        {"Input": "Room temperature", "Status": "Datasheets list 20 to 30 degrees"},
        {"Input": "Heat stored in the incubator", "Status": "Assumption"},
        {"Input": "Battery usable share (80 percent)", "Status": "Cited for lithium batteries (2017 review), at a cost in battery life"},
        {"Input": "Converter efficiency (90 percent)", "Status": "Slightly optimistic for a small load (inverter idle draw)"},
        {"Input": "Charger power (200 W)", "Status": "Assumption; it must be able to refill the battery between outages"},
        {"Input": "Outage patterns", "Status": "Ranges from sensor studies in Sierra Leone and DR Congo, not one dataset"},
    ])
