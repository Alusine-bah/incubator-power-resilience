"""Grid with outages plus solar: how much does a small solar array shrink the incubator's battery?

The grid runs the incubator when it is on; during an outage solar runs it first and the battery
covers the rest. Between outages the grid charger and the solar refill the battery. Hourly solar
output is the measured PVGIS record in data/ (10 years). Outages are random, drawn from published
ranges (Sierra Leone sensor study: 0.6 to 3.1 outages a day; outage lengths as in uncertainty.py),
and the same outage draws are used at every site. Because the battery is set by the worst cluster
of outages in 10 years, each case is repeated with 5 outage draws; the table shows the median and range.
Saves docs/grid_solar.png.
"""
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from model import Params
from solar import (SITES, SITE_LABEL, SolarSetup, battery_side_load_w, data_path, grid_gains, load_site,
                   outage_fraction, storage_from_gains)

SCENARIOS = (("moderate", 2.0, 1.5), ("severe", 3.0, 2.0))   # outages a day, median length (h)
CHARGERS = (200.0, 60.0, 0.0)
ARRAYS_KWP = (0.0, 0.5, 1.0, 1.5, 2.0)
SEEDS = (2026, 2027, 2028, 2029, 2030)


def rated_kwh(pv, load, outage, kwp, charger, p, s):
    gains = grid_gains(pv * kwp, load, outage, charger, p.efficiency, s.charge_efficiency)
    return storage_from_gains(gains) / p.usable_fraction / 1000.0


def cell(values, load_w):
    med = float(np.median(values))
    if med * 1000 / (load_w * 24.0) > 7:
        return f"{'impractical':^18}"
    return f"{f'{med:.1f} ({min(values):.1f}-{max(values):.1f})':^18}"


def main():
    t0 = time.time()
    p = Params()
    s = SolarSetup()
    load = float(battery_side_load_w(p, p.room_c, s))
    sites = [x[0] for x in SITES if os.path.exists(data_path(x[0]))]
    if not sites:
        print("No solar data found. Run: python get_solar_data.py")
        return
    print("Grid with outages plus solar: rated battery (kWh) so the incubator never loses power in 10 years")
    print(f"Default incubator, 2 kg baby, 22 C room: {load:.0f} W from the battery side. 80 percent usable.")
    print("Each cell: median of 5 random outage draws (lowest-highest). 'impractical' = more than a week of storage.")
    print("Charger: grid charger power in W (0 = the battery is charged only by the solar array).")
    print()
    n = len(load_site(sites[0])[1])
    outages = {}
    for name, per_day, med in SCENARIOS:
        outages[name] = [outage_fraction(n, per_day, med, seed=sd) for sd in SEEDS]
        hrs = np.mean([o.sum() / (n / 24.0) for o in outages[name]])
        print(f"Outage scenario '{name}': {per_day:g} a day on average, median length {med:g} h, "
              f"about {hrs:.1f} h a day without grid power")
    print()

    curves = {}
    for site in sites:
        stamp, pv, outdoor = load_site(site)
        print(f"== {SITE_LABEL[site]} ==")
        for name, per_day, med in SCENARIOS:
            print(f"   {name + ' outages, kWp:':<22}|" + "|".join(f"{k:^18.1f}" for k in ARRAYS_KWP))
            for ch in CHARGERS:
                vals = [[rated_kwh(pv, load, o, k, ch, p, s) for o in outages[name]] for k in ARRAYS_KWP]
                curves[(site, name, ch)] = [float(np.median(v)) for v in vals]
                print(f"   {f'charger {ch:.0f} W':<22}|" + "|".join(cell(v, load) for v in vals))
        print()

    first = sites[0]
    base = curves[(first, "moderate", 200.0)]
    print(f"{SITE_LABEL[first]}, moderate outages, 200 W charger: 0.5 kWp of solar shrinks the battery from "
          f"{base[0]:.1f} to {base[1]:.1f} kWh ({100 * (1 - base[1] / base[0]):.0f} percent smaller); 1 kWp to {base[2]:.1f} kWh.")
    weak = curves[(first, "moderate", 60.0)]
    print(f"   With a 60 W charger: {weak[0]:.1f} kWh without solar, {weak[1]:.1f} kWh with 0.5 kWp.")

    os.makedirs("docs", exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    for ch, style in zip(CHARGERS, ("-", "--", ":")):
        y = curves[(first, "moderate", ch)]
        ax[0].plot(ARRAYS_KWP, y, style, marker="o", label=f"grid charger {ch:.0f} W" if ch else "no grid charger")
    ax[0].set_yscale("log")
    ax[0].set_xlabel("Solar array (kWp)")
    ax[0].set_ylabel("Rated battery (kWh)")
    ax[0].set_title(f"{SITE_LABEL[first].split(',')[0]}, moderate outages: charger and solar")
    ax[0].grid(alpha=0.3, which="both")
    ax[0].legend(fontsize=8)
    for site in sites:
        ax[1].plot(ARRAYS_KWP, curves[(site, "moderate", 200.0)], marker="o", label=SITE_LABEL[site])
    ax[1].set_xlabel("Solar array (kWp)")
    ax[1].set_ylabel("Rated battery (kWh)")
    ax[1].set_title("All sites, moderate outages, 200 W charger")
    ax[1].set_ylim(bottom=0)
    ax[1].grid(alpha=0.3)
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    try:
        fig.savefig("docs/grid_solar.png", dpi=130)
    except OSError:
        print("Could not save docs/grid_solar.png. Close the picture if it is open in an image viewer, then run again.")
        return
    print()
    print(f"Saved docs/grid_solar.png ({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
