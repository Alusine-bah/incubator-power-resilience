"""How large a solar array and battery does one incubator need to run off-grid?

Uses 10 years of measured hourly solar output (PVGIS, saved by get_solar_data.py) for each site.
For each array size, finds the smallest battery that never runs empty in any hour of the record.
Saves docs/solar_sizing.png. The default case is the measured-heat-loss incubator, a 2 kg baby
and a 22 C room; a second case lets the room follow the outdoor air temperature.
"""
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from model import Params
from solar import (longest_run, missing_hours, load_site_raw, SITES, SITE_LABEL, SITE_UTC_OFFSET, SolarSetup, battery_side_load_w, data_path,
                   load_site, monthly_yield_kwh_per_kwp_day, run_hourly, size_battery,
                   usable_storage_needed_wh, years_and_months)

ARRAYS_KWP = (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0)
NIGHT_KWP = 50.0      # an array so large that only the night-time need remains
SHOW_KWP = 2.5        # array used for the worst-week example
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def fmt(rated_wh, load_w):
    """Battery size, flagged when it would have to store more than a week of incubator energy."""
    days = rated_wh / (load_w * 24.0)
    text = f"{rated_wh / 1000:6.1f} kWh"
    return text + (f" = {days:.0f} days of use, impractical" if days > 7 else "")


def per_year_rated(pv, load, kwp, s, usable_fraction, years):
    """Battery needed in each calendar year on its own (starting full on 1 January)."""
    out = []
    for y in np.unique(years):
        sel = years == y
        if sel.sum() < 8000:
            continue
        ld = load[sel] if np.ndim(load) else load
        out.append(usable_storage_needed_wh(pv[sel] * kwp, ld, s.charge_efficiency) / usable_fraction)
    return np.array(out)


def main():
    t0 = time.time()
    p = Params()
    s = SolarSetup()
    load_fixed = float(battery_side_load_w(p, p.room_c, s))
    sites = [x[0] for x in SITES if os.path.exists(data_path(x[0]))]
    if not sites:
        print("No solar data found. Run: python get_solar_data.py")
        return

    print("Off-grid incubator: solar array and battery sizing")
    print(f"Incubator: heat loss {p.ua} W/C, heater {p.heater_w:.0f} W, 2 kg baby, air setpoint {p.setpoint_c:.1f} C.")
    print(f"Room fixed at {p.room_c:.0f} C: incubator draws {load_fixed:.0f} W from the solar side, "
          f"{load_fixed * 24 / 1000:.2f} kWh per day (converter {p.efficiency:.0%}, charging {s.charge_efficiency:.0%}).")
    print(f"Battery sizes are rated capacity at {p.usable_fraction:.0%} usable, for no hour without power in the whole record.")
    print("Solar data: PVGIS hourly output of a 1 kWp array at the optimal tilt, after 14 percent system losses.")
    print()

    curves = {}
    yields = {}
    for site in sites:
        stamp, pv, outdoor = load_site(site)
        years, months = years_and_months(stamp)
        y = monthly_yield_kwh_per_kwp_day(stamp, pv)
        yields[site] = y
        load_out = battery_side_load_w(p, outdoor, s)
        worst = int(np.argmin(y))
        raw_stamp, raw_pv, _ = load_site_raw(site)
        miss = missing_hours(raw_stamp, raw_pv)
        print(f"== {SITE_LABEL[site]} ({years.min()}-{years.max()}, {len(np.unique(years))} years) ==")
        whole = sorted({raw_stamp[i][:8] for i in np.nonzero(miss)[0]
                        if miss[(np.array([x[:8] for x in raw_stamp]) == raw_stamp[i][:8])].sum() >= 8})
        print(f"   satellite gaps filled: {int(miss.sum())} hours (longest run {longest_run(miss)} hours"
              + (f"; days with 8 or more missing hours: {', '.join(d[:4] + '-' + d[4:6] + '-' + d[6:] for d in whole[:8])}"
                 + (' ...' if len(whole) > 8 else '') if whole else "") + ")")
        print(f"   solar yield: {pv.sum() / 1000 / (len(pv) / 8760):.0f} kWh per kWp per year; "
              f"worst month {MONTHS[worst]} {y[worst]:.2f}, best {MONTHS[int(np.argmax(y))]} {y.max():.2f} kWh per kWp per day")
        print(f"   room follows outdoor air: mean outdoor {outdoor.mean():.1f} C, incubator draws {load_out.mean():.0f} W on average")
        print("   array (kWp) | battery, room 22 C: whole record (typical single year) | battery, room = outdoor air")
        rows = []
        for kwp in ARRAYS_KWP:
            rated = size_battery(pv, load_fixed, kwp, s, p.usable_fraction)
            yearly = per_year_rated(pv, np.full(len(pv), load_fixed), kwp, s, p.usable_fraction, years)
            rated_out = size_battery(pv, load_out, kwp, s, p.usable_fraction)
            rows.append(rated)
            print(f"   {kwp:9.1f}   | {fmt(rated, load_fixed)} ({np.median(yearly) / 1000:.1f} kWh)"
                  f"  | {fmt(rated_out, float(load_out.mean()))}")
        night = size_battery(pv, load_fixed, NIGHT_KWP, s, p.usable_fraction)
        print(f"   night-time floor (very large array): {night / 1000:.1f} kWh")
        curves[site] = (np.array(rows), night)
        print()

    ft = sites[0]
    stamp, pv, outdoor = load_site(ft)
    rated = size_battery(pv, load_fixed, SHOW_KWP, s, p.usable_fraction)
    charge, unmet = run_hourly(pv * SHOW_KWP, load_fixed, rated * p.usable_fraction, s.charge_efficiency)
    lowest = int(np.argmin(charge))
    a = max(0, lowest - 24 * 5)
    b = min(len(pv), lowest + 24 * 2)
    print(f"Worst week, {SITE_LABEL[ft]}, {SHOW_KWP} kWp with a {rated / 1000:.1f} kWh battery: "
          f"lowest charge on {stamp[lowest][:4]}-{stamp[lowest][4:6]}-{stamp[lowest][6:8]}; "
          f"hours without power in the whole record: {int((unmet > 0.01).sum())}")
    smaller = rated * 0.75
    _, unmet75 = run_hourly(pv * SHOW_KWP, load_fixed, smaller * p.usable_fraction, s.charge_efficiency)
    days75 = len({stamp[i][:8] for i in np.nonzero(unmet75 > 0.01)[0]})
    print(f"   with a battery 25 percent smaller ({smaller / 1000:.1f} kWh): {int((unmet75 > 0.01).sum())} hours "
          f"without power on {days75} days in {len(pv) / 8760:.0f} years")

    os.makedirs("docs", exist_ok=True)
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
    for site in sites:
        ax[0].plot(range(1, 13), yields[site], marker="o", label=SITE_LABEL[site])
        ax[1].plot(ARRAYS_KWP, curves[site][0] / 1000, marker="o", label=SITE_LABEL[site])
    ax[0].set_xticks(range(1, 13))
    ax[0].set_xticklabels([m[0] for m in MONTHS])
    ax[0].set_ylabel("kWh per kWp per day")
    ax[0].set_title("Solar output by month (PVGIS)")
    ax[0].grid(alpha=0.3)
    ax[0].legend(fontsize=7)
    ax[1].set_xlabel("Solar array (kWp)")
    ax[1].set_ylabel("Rated battery (kWh)")
    ax[1].set_title("Battery so the incubator never loses power")
    ax[1].set_yscale("log")
    ax[1].grid(alpha=0.3, which="both")
    off = SITE_UTC_OFFSET[ft]
    hrs = (np.arange(a, b) - a) / 24.0
    ax[2].plot(hrs, pv[a:b] * SHOW_KWP, color="tab:orange", lw=0.8, label="solar output (W)")
    ax[2].axhline(load_fixed, color="black", ls=":", label="incubator draw (W)")
    ax[2].set_ylabel("Power (W)")
    ax2 = ax[2].twinx()
    ax2.plot(hrs, charge[a:b] / 1000, color="tab:green", label="battery charge (kWh)")
    ax2.set_ylabel("Battery charge (kWh)")
    ax2.set_ylim(bottom=0)
    ax[2].set_xlabel(f"Days (starting {stamp[a][:4]}-{stamp[a][4:6]}-{stamp[a][6:8]}, UTC{off:+d})")
    ax[2].set_title(f"Hardest week, {SITE_LABEL[ft].split(',')[0]}: {SHOW_KWP} kWp, {rated / 1000:.1f} kWh")
    h1, l1 = ax[2].get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax[2].legend(h1 + h2, l1 + l2, fontsize=7, loc="upper left")
    fig.tight_layout()
    try:
        fig.savefig("docs/solar_sizing.png", dpi=130)
    except OSError:
        print("Could not save docs/solar_sizing.png. Close the picture if it is open in an image viewer, then run again.")
        return
    print()
    print(f"Saved docs/solar_sizing.png ({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
