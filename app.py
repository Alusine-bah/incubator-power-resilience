import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os
from model import Params, grid_profile, repeated_outages, simulate, setpoint_for_weight
from solar import (SITES, SITE_LABEL, SolarSetup, battery_side_load_w, data_path, grid_gains, load_site,
                   monthly_yield_kwh_per_kwp_day, outage_fraction, run_gains, storage_from_gains)

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

tab_sim, tab_solar, tab_sure = st.tabs(["Power failure", "Solar sizing", "How sure? (2,000 cases)"])

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


with tab_sim:
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

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


@st.cache_data
def site_data(site):
    stamp, pv, outdoor = load_site(site)
    return stamp, pv, outdoor, monthly_yield_kwh_per_kwp_day(stamp, pv)


@st.cache_data
def outages(n, per_day, median_h):
    return outage_fraction(n, per_day, median_h, seed=2026)


with tab_solar:
    st.subheader("How large a solar array and battery does one incubator need?")
    st.caption(
        "Solar output is measured hour by hour over 10 years (PVGIS, European Commission JRC) for a 1 kWp array at "
        "the best tilt, after 14 percent system losses. The incubator and baby settings come from the sidebar; each "
        "hour the heater uses what holds the air at its setpoint. Hours where the satellite record shows exactly zero "
        "at a time of day that is almost never dark are treated as gaps and filled with the typical output for that "
        "month and hour."
    )
    have = [s[0] for s in SITES if os.path.exists(data_path(s[0]))]
    if not have:
        st.warning("No solar data yet. Run python get_solar_data.py once, then reload.")
    else:
        supply = st.radio("Power supply", ["Off-grid: solar and battery only", "Grid with outages, plus solar"],
                          horizontal=True,
                          help="Off-grid: as at the off-grid hospitals in the Sierra Leone sensor study. Grid with "
                               "outages: the grid runs the incubator when it is on; during an outage solar runs it "
                               "first and the battery covers the rest.")
        grid_mode = supply.startswith("Grid")
        c1, c2, c3 = st.columns(3)
        site = c1.selectbox("Site", have, format_func=lambda s: SITE_LABEL[s])
        kwp = c2.slider("Solar array (kWp)", 0.0, 8.0, 1.0 if grid_mode else 2.5, 0.1,
            help="Peak power of the panels. 1 kWp is roughly three typical 330 to 400 W panels.")
        batt_kwh = c3.slider("Battery (kWh, rated)", 1.0, 30.0, 4.0 if grid_mode else 13.0, 0.5,
            help="Rated capacity; 80 percent is treated as usable, as in the rest of the model.")
        d1, d2 = st.columns(2)
        follow = d1.checkbox("Room follows the outdoor air temperature", value=False,
            help="Off: the room stays at the sidebar temperature. On: the room equals the outdoor air temperature "
                 "from the same dataset, hour by hour. That is an assumption for an unventilated, unheated ward; "
                 "measured ward temperatures were not found.")
        other = d2.slider("Fan and electronics (W)", 0, 100, 0, 5,
            help="Not measured in the sources used, so the default is 0. Try values to see how much it adds.")
        stamp, pv, outdoor, yields = site_data(site)
        n = len(pv)
        if grid_mode:
            g1, g2, g3 = st.columns(3)
            per_day = g1.slider("Outages a day (average)", 0.5, 4.0, 2.0, 0.1,
                help="The Sierra Leone sensor study recorded 0.6 to 3.1 outages a day at 15 facilities.")
            med_h = g2.slider("Typical outage length (median, hours)", 0.5, 4.0, 1.5, 0.1,
                help="Lengths vary at random around this median (lognormal, 0.25 to 11 hours), as in the "
                     "uncertainty analysis. North Kivu facilities averaged a median outage of 2.0 hours.")
            grid_charger = g3.slider("Grid charger (W)", 0, 500, 200, 10,
                help="Charges the battery whenever the grid is on. 0 means the battery is charged only by the solar array.")
            out = outages(n, float(per_day), float(med_h))
            st.caption(f"These random outages leave the incubator without grid power {out.sum() / (n / 24):.1f} hours "
                       "a day on average. The outages are one random draw (seed 2026), the same at every site; "
                       "the battery is set by the worst cluster of outages in 10 years.")
        else:
            out = np.ones(n)
            grid_charger = 0.0
        p = Params(heater_w=float(heater), ua=float(ua), room_c=float(room), air_capacity=cap * 1000.0,
                   baby_mass_kg=float(weight), metabolic_w_per_kg=float(meta))
        s = SolarSetup(other_load_w=float(other))
        load = battery_side_load_w(p, outdoor if follow else p.room_c, s)
        load_arr = np.broadcast_to(np.asarray(load, dtype=float), pv.shape)

        def need_kwh(k):
            gains = grid_gains(pv * k, load_arr, out, float(grid_charger), p.efficiency, s.charge_efficiency)
            return storage_from_gains(gains) / p.usable_fraction / 1000.0

        need_rated = need_kwh(kwp) * 1000.0
        gains = grid_gains(pv * kwp, load_arr, out, float(grid_charger), p.efficiency, s.charge_efficiency)
        steps, unmet_steps = run_gains(gains, batt_kwh * 1000 * p.usable_fraction)
        charge = steps[1::2]
        unmet = unmet_steps.reshape(-1, 2).sum(axis=1)
        lost = np.nonzero(unmet > 0.01)[0]
        lost_days = len({stamp[i][:8] for i in lost})
        years = n / 8760.0
        worst = int(np.argmin(yields))

        m1, m2, m3 = st.columns(3)
        m1.metric("Incubator energy per day", f"{load_arr.mean() * 24 / 1000:.2f} kWh",
                  help="Average draw from the battery side, including the 90 percent converter.")
        m2.metric("Battery this design needs", f"{need_rated / 1000:.1f} kWh",
                  help="Smallest rated battery with no hour without power in the whole record.")
        m3.metric(f"Hours without power in {years:.0f} years", f"{len(lost)}",
                  help="With the battery chosen above.")
        if len(lost) == 0:
            st.success(f"With {kwp:.1f} kWp and {batt_kwh:.1f} kWh the incubator never lost power in "
                       f"{years:.0f} years of measured weather at {SITE_LABEL[site]}.")
        else:
            st.error(f"The incubator lost power for {len(lost)} hours on {lost_days} days in {years:.0f} years. "
                     f"Without power its air cools and the baby with it (see the first tab).")
        if need_rated / (load_arr.mean() * 24) > 7:
            st.warning("This design cannot keep up: the battery would have to store more than a week of energy. "
                       "Add panels or a stronger charger instead.")
        st.caption(f"Worst month for solar here: {MONTHS[worst]}, {yields[worst]:.2f} kWh per kWp per day "
                   f"(best {MONTHS[int(np.argmax(yields))]}, {yields.max():.2f}).")

        sizes = np.round(np.arange(0.0 if grid_mode else 1.0, 8.01, 0.5 if grid_mode else 0.25), 2)
        curve = [need_kwh(k) for k in sizes]
        lowest = int(np.argmin(charge))
        a = max(0, lowest - 24 * 5)
        b = min(n, lowest + 24 * 2)
        fig2, ax2 = plt.subplots(1, 3, figsize=(15, 4))
        ax2[0].bar(range(1, 13), yields, color="tab:orange")
        ax2[0].set_xticks(range(1, 13))
        ax2[0].set_xticklabels([m[0] for m in MONTHS])
        ax2[0].set_ylabel("kWh per kWp per day")
        ax2[0].set_title("Solar output by month")
        ax2[1].plot(sizes, curve, marker=".")
        ax2[1].plot([kwp], [need_rated / 1000], "o", color="tab:red", label="your array")
        ax2[1].axhline(batt_kwh, color="gray", ls=":", label="your battery")
        ax2[1].set_yscale("log")
        ax2[1].set_xlabel("Solar array (kWp)")
        ax2[1].set_ylabel("Battery needed (kWh, rated)")
        ax2[1].set_title("Trade-off: panels against battery")
        ax2[1].grid(alpha=0.3, which="both")
        ax2[1].legend(fontsize=8)
        hrs = (np.arange(a, b) - a) / 24.0
        if grid_mode:
            ax2[2].fill_between(hrs, 0, out[a:b] * max(1.0, (pv[a:b] * kwp).max(), load_arr[a:b].max()),
                                step="mid", color="lightgray", label="grid outage")
        ax2[2].plot(hrs, pv[a:b] * kwp, color="tab:orange", lw=0.8, label="solar (W)")
        ax2[2].plot(hrs, load_arr[a:b], color="black", ls=":", label="incubator (W)")
        ax2[2].set_ylabel("Power (W)")
        ax2[2].set_xlabel(f"Days from {stamp[a][:4]}-{stamp[a][4:6]}-{stamp[a][6:8]} (UTC)")
        tw = ax2[2].twinx()
        tw.plot(hrs, charge[a:b] / 1000, color="tab:green", label="battery (kWh)")
        tw.set_ylim(bottom=0)
        tw.set_ylabel("Battery charge (kWh)")
        ax2[2].set_title("Hardest week in the record, your design")
        h1, l1 = ax2[2].get_legend_handles_labels()
        h2, l2 = tw.get_legend_handles_labels()
        ax2[2].legend(h1 + h2, l1 + l2, fontsize=7, loc="upper left")
        fig2.tight_layout()
        st.pyplot(fig2)
        st.caption(
            "Limits: the load is the heater only (plus the fan slider); battery ageing, panel dirt beyond the "
            "PVGIS loss, and other equipment sharing the system are not modelled. Real systems are usually "
            "oversized for these. Sizes are for one incubator. In grid mode the outages are random and spread "
            "evenly over the day and year; real outages may cluster in the evening peak or the dry season, and "
            "low voltage without a full outage is not included here."
        )


CASES = os.path.join("docs", "uncertainty_cases.csv")


@st.cache_data
def load_cases():
    return np.genfromtxt(CASES, delimiter=",", names=True)


with tab_sure:
    st.subheader("How sure are the battery sizes? 2,000 random cases")
    st.caption(
        "Each case draws every uncertain input at random from its published range (heat loss, baby heat production, "
        "room temperature, heat stored, heater, converter efficiency, grid voltage, outage length) for a 2 kg baby, "
        "using uncertainty.py (seed 2026). The sidebar settings do not change these cases."
    )
    if not os.path.exists(CASES):
        st.warning("No case file yet. Run python uncertainty.py once (about 4 minutes), then reload.")
    else:
        cs = load_cases()
        u1, u2, u3 = st.columns(3)
        battery_wh = u1.slider("Battery (Wh, rated)", 100, 3000, 500, 50)
        how = u2.radio("Outage length", ["Random, from the published range", "Fixed"],
                       help="Random: each case has its own outage length (median 1.5 h, 0.25 to 11 h).")
        fixed_h = u2.slider("Fixed outage length (hours)", 0.5, 11.0, 2.0, 0.5, disabled=how.startswith("Random"))
        room_lo, room_hi = u3.slider("Only rooms between (" + D + ")", 20.0, 30.0, (20.0, 30.0), 0.5,
            help="Room temperature matters more than any other input. Narrow this to see a warm or a cold ward.")
        sel = (cs["room"] >= room_lo) & (cs["room"] <= room_hi)
        per_hour = cs["battery_per_outage_hour_wh"][sel]
        hours = cs["outage_hours"][sel] if how.startswith("Random") else np.full(sel.sum(), fixed_h)
        need = per_hour * hours
        cold = cs["lowest_core_2h_no_backup_c"][sel]
        if sel.sum() < 20:
            st.warning("Fewer than 20 cases in this room range; widen it.")
        else:
            k1, k2, k3 = st.columns(3)
            k1.metric("Cases this battery covers", f"{100 * np.mean(need <= battery_wh):.0f}%",
                      help=f"Out of {sel.sum()} cases in the chosen room range.")
            k2.metric("Battery per outage hour (median)", f"{np.median(per_hour):.0f} Wh",
                      help=f"5th to 95th percentile: {np.percentile(per_hour, 5):.0f} to {np.percentile(per_hour, 95):.0f} Wh.")
            k3.metric("Battery covering 95% of cases", f"{np.percentile(need, 95):.0f} Wh")
            st.caption(f"No backup, 2 h blackout: in these cases the baby's lowest modelled temperature has a median of "
                       f"{np.median(cold):.1f} {D} and falls below 32 {D} in {100 * np.mean(cold < 32):.0f}% of them.")
            fig3, ax3 = plt.subplots(1, 2, figsize=(12, 4))
            ax3[0].hist(need, bins=40, color="tab:blue")
            ax3[0].axvline(battery_wh, color="tab:red", label="your battery")
            ax3[0].set_xlabel("Rated battery each case needs (Wh)")
            ax3[0].set_ylabel("Number of cases")
            ax3[0].set_title("Battery needed")
            ax3[0].legend(fontsize=8)
            xs = np.linspace(0, max(3000, np.percentile(need, 99)), 300)
            ax3[1].plot(xs, [100 * np.mean(need <= x) for x in xs], color="tab:green")
            ax3[1].axvline(battery_wh, color="tab:red", ls=":")
            ax3[1].set_xlabel("Rated battery (Wh)")
            ax3[1].set_ylabel("Cases covered (%)")
            ax3[1].set_title("Coverage")
            ax3[1].grid(alpha=0.3)
            fig3.tight_layout()
            st.pyplot(fig3)
            st.caption("The input ranges for heat loss, room temperature and outage length are my choices, centred "
                       "on or spanning published values (see PARAMETERS.md), so these shares hold only given them.")
