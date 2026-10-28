import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from model import Params, grid_profile, repeated_outages, simulate

D = "\u00b0C"

st.set_page_config(page_title="Incubator power-failure simulator", layout="wide")
st.title("Infant incubator: what happens to the baby when the power fails?")
st.caption(
    "A simple educational simulation of an incubator, a 2 kg preterm baby and a backup battery. "
    "Most inputs are assumptions (see the table at the bottom). This is not a medical device "
    "and must not be used for clinical decisions."
)

st.warning(
    "Provisional numbers: the default heat loss (5 W per " + D + ") is about a third of the value measured on one commercial incubator "
    "(about 15 W per " + D + ", see PARAMETERS.md). Battery sizes at the default are likely too small for such a device. "
    "Move the heat-loss slider to 15 to see the effect. Update in progress."
)

sb = st.sidebar
sb.header("1. The incubator")
heater = sb.slider("Heater power (W)", 150, 500, 300, 25,
    help="Heater power at full voltage. 300 W is the default because a 200 W heater cannot meet the 20-minute warm-up of a commercial unit (VNG 3000 datasheet).")
ua = sb.slider("Heat leaking to the room (W per " + D + ")", 2.0, 20.0, 5.0, 0.5,
    help="Watts lost for every degree the incubator is warmer than the room. Default 5. Two papers calculate about 3.8 and 4.2 (neither measured). This is the number that changes the battery size most.")
room = sb.slider("Room temperature (" + D + ")", 16, 30, 22,
    help="Datasheets list 20 to 30 degrees. Below 20 is a stress test.")
cap = sb.slider("Heat stored in the incubator (kJ per " + D + ")", 5, 30, 20,
    help="Assumption. It does not change the battery size, but it changes how fast an unprotected incubator cools.")

sb.header("2. The baby")
meta = sb.slider("Baby's own heat production (W)", 2.0, 4.0, 3.0, 0.5,
    help="Assumption. The baby's heat loss is set so the baby balances at 37.0 degrees in 33.5 degree air.")

sb.header("3. The backup battery")
rating = sb.slider("Battery size (Wh)", 0, 900, 300, 25,
    help="Rated capacity. Only 80 percent is treated as usable and the converter is 90 percent efficient (both assumptions).")
trigger = sb.slider("Low-voltage trigger (" + D + " below setpoint)", 0.2, 1.0, 0.6, 0.1,
    help="During low voltage (not a full blackout) the battery takes over when the incubator air falls this far below the 33.5 degree setpoint. Keep it above 0.5, because the thermostat normally swings 0.5 either side of the setpoint.")
charger = sb.slider("Charger power (W)", 20, 200, 60, 10, help="Assumption.")

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
def run_case(heater, ua, room, cap, meta, trigger, charger, scenario, length, vfrac, rating):
    p = Params(heater_w=float(heater), ua=float(ua), room_c=float(room),
               air_capacity=cap * 1000.0, metabolic_w=float(meta),
               trigger_drop_c=float(trigger), charger_w=float(charger))
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
    return grid, simulate(p, grid, rating), simulate(p, grid, 0)


grid, with_b, without = run_case(heater, ua, room, cap, meta, trigger, charger,
                                 scenario, length, vfrac, rating)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Lowest baby temperature, with backup", f"{with_b['lowest_core']:.2f} {D}")
c2.metric("Lowest baby temperature, no backup", f"{without['lowest_core']:.2f} {D}")
c3.metric("Minutes below 36.5 " + D + ", with backup", f"{with_b['minutes_core_below_36_5']:.0f}")
c4.metric("Battery energy used", f"{with_b['battery_used_wh']:.0f} Wh")
c5.metric("Minutes the battery was empty", f"{with_b['minutes_battery_empty']:.0f}")

if with_b["minutes_battery_empty"] > 0:
    st.error("The battery ran out during a blackout, so the baby lost its heating.")
elif with_b["lowest_core"] < 36.5:
    st.warning("The baby's modelled temperature fell below 36.5 " + D + ".")
else:
    st.success("With this backup, the baby's modelled temperature stayed at or above 36.5 " + D + ".")

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
ax[1].axhline(33.5, color="gray", ls=":")
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
        "Heat exchange with the cooling walls, which probably makes the baby cool too slowly in the model. "
        "The baby's own response to cold, which probably makes it cool too fast. The two effects pull in "
        "opposite directions and the net effect is unknown. Also left out: the fan and electronics load, "
        "battery ageing, short sags and surges, and clustered outages. "
        "The heater is a fixed resistance, and the fan and controller are assumed to keep running at low voltage."
    )

with st.expander("Which inputs have a source?"):
    st.table([
        {"Input": "Heater power", "Status": "Checked against one datasheet warm-up spec"},
        {"Input": "Heat leaking to the room", "Status": "Plausible: two calculated values (3.8 and 4.2), none measured"},
        {"Input": "Room temperature", "Status": "Datasheets list 20 to 30 degrees"},
        {"Input": "Air setpoint 33.5 degrees", "Status": "Hospital guideline for a 2 kg baby; a handbook chart gives 31 to 34"},
        {"Input": "Heat stored in the incubator", "Status": "Assumption"},
        {"Input": "Baby heat production and loss", "Status": "Assumption (set so the baby balances at 37.0)"},
        {"Input": "Battery efficiency, usable share, charger", "Status": "Assumptions"},
        {"Input": "Outage patterns", "Status": "Ranges from sensor studies in Sierra Leone and DR Congo, not one dataset"},
    ])
