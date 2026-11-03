"""Off-grid solar sizing for one incubator: how big a solar panel and battery keep it running?

The incubator here runs only from solar panels and a battery (no grid), as at the off-grid
hospitals in the Sierra Leone sensor study. Time steps are one hour, using measured hourly
solar output from PVGIS for a 1 kWp array at each site.

Hourly load. Over an hour the thermostat holds the air at its setpoint, so the heater's
average power equals the heat leaking to the room:
    heater (W) = heat loss x (setpoint - room), between 0 and the heater rating.
As in model.py, the baby's own heat (about 4 W for a 2 kg baby) is not added to the air, which
makes the load about 2 percent conservative.
The battery side also pays the converter loss (efficiency) and any fan or electronics load.
check_model.py confirms this against the second-by-second model in model.py.

Battery. Starts full. Solar first runs the incubator; any surplus charges the battery at the
charging efficiency; any shortfall comes out of the battery. The smallest battery that never
runs empty is found in one pass (the deepest cumulative drawdown below full).
"""
import gzip
import os
from dataclasses import dataclass

import numpy as np

from model import Params

DATA_DIR = "data"

# Sites: name, label, latitude, longitude, hours ahead of UTC (for daily plots only).
SITES = (
    ("freetown", "Freetown, Sierra Leone", 8.484, -13.234, 0),
    ("bonthe", "Bonthe, Sierra Leone", 7.526, -12.505, 0),
    ("kabala", "Kabala, Sierra Leone", 9.589, -11.553, 0),
    ("goma", "Goma, North Kivu, DR Congo", -1.650, 29.230, 2),
    ("dhaka", "Dhaka, Bangladesh", 23.810, 90.412, 6),
)
SITE_LABEL = {s[0]: s[1] for s in SITES}
SITE_UTC_OFFSET = {s[0]: s[4] for s in SITES}


@dataclass(frozen=True)
class SolarSetup:
    charge_efficiency: float = 0.95   # assumption: solar charge controller and lithium battery charging
    other_load_w: float = 0.0         # fan and electronics; not measured in the sources used, so 0 by default


def heater_average_w(p: Params, room_c):
    """Average heater power (W) that holds the setpoint, for a room temperature (scalar or array)."""
    need = p.ua * (p.setpoint_c - np.asarray(room_c, dtype=float))
    return np.clip(need, 0.0, p.heater_w)


def battery_side_load_w(p: Params, room_c, s: SolarSetup = SolarSetup()):
    """Power drawn from the solar and battery side (W), after the converter loss."""
    return heater_average_w(p, room_c) / p.efficiency + s.other_load_w


def usable_storage_needed_wh(pv_w, load_w, charge_efficiency):
    """Smallest usable battery (Wh) that never runs empty, starting full. Hourly steps."""
    pv = np.asarray(pv_w, dtype=float)
    load = np.broadcast_to(np.asarray(load_w, dtype=float), pv.shape)
    net = pv - load                       # Wh in each hour (W x 1 h)
    gain = np.where(net > 0, net * charge_efficiency, net)
    deficit = 0.0
    worst = 0.0
    for g in gain.tolist():
        deficit -= g
        if deficit < 0.0:
            deficit = 0.0
        elif deficit > worst:
            worst = deficit
    return worst


def storage_from_gains(gains):
    """Smallest usable battery (Wh) that never runs empty, starting full, for a sequence of energy gains (Wh)."""
    deficit = 0.0
    worst = 0.0
    for g in np.asarray(gains, dtype=float).tolist():
        deficit -= g
        if deficit < 0.0:
            deficit = 0.0
        elif deficit > worst:
            worst = deficit
    return worst


def run_gains(gains, usable_wh):
    """Battery charge after each step and the energy each step could not supply, for a given usable battery."""
    soc = usable_wh
    g = np.asarray(gains, dtype=float)
    charge = np.empty(len(g))
    unmet = np.zeros(len(g))
    for i, x in enumerate(g.tolist()):
        soc += x
        if soc > usable_wh:
            soc = usable_wh
        elif soc < 0.0:
            unmet[i] = -soc
            soc = 0.0
        charge[i] = soc
    return charge, unmet


def outage_fraction(n_hours, per_day, median_h, sigma=0.9, min_h=0.25, max_h=11.0, seed=2026):
    """Share of each hour without grid power, from random outages.

    Outage starts are random in time (on average per_day a day); lengths are lognormal with the
    given median, limited to min_h to max_h, as in uncertainty.py. Overlapping outages merge.
    Resolution one minute. Seeded, so the same settings always give the same outages.
    """
    rng = np.random.default_rng(seed)
    minutes = n_hours * 60
    off = np.zeros(minutes, dtype=bool)
    t = rng.exponential(24.0 / per_day) if per_day > 0 else n_hours
    while t < n_hours:
        length = float(np.clip(rng.lognormal(np.log(median_h), sigma), min_h, max_h))
        a = int(t * 60)
        off[a:min(minutes, a + int(round(length * 60)))] = True
        t += rng.exponential(24.0 / per_day)
    return off.reshape(n_hours, 60).mean(axis=1)


def grid_gains(pv_w, load_w, outage, charger_w, converter_efficiency, charge_efficiency):
    """Battery energy gains (Wh) in two steps per hour: the outage part first, then the grid part.

    Outage part: solar runs the incubator, any surplus charges the battery, the battery covers the rest.
    Grid part: the grid runs the incubator, and the grid charger and the solar both charge the battery.
    Putting the outage first in each hour is the cautious order.
    """
    pv = np.asarray(pv_w, dtype=float)
    load = np.broadcast_to(np.asarray(load_w, dtype=float), pv.shape)
    o = np.asarray(outage, dtype=float)
    net = (pv - load) * o
    out_part = np.where(net > 0, net * charge_efficiency, net)
    grid_part = (charger_w * converter_efficiency + pv * charge_efficiency) * (1.0 - o)
    return np.column_stack([out_part, grid_part]).ravel()


def run_hourly(pv_w, load_w, usable_wh, charge_efficiency):
    """Hour-by-hour battery charge (Wh) and unmet load (Wh) for a given usable battery."""
    pv = np.asarray(pv_w, dtype=float)
    load = np.broadcast_to(np.asarray(load_w, dtype=float), pv.shape)
    soc = usable_wh
    charge = np.empty(len(pv))
    unmet = np.zeros(len(pv))
    for i in range(len(pv)):
        net = pv[i] - load[i]
        if net >= 0:
            soc = min(usable_wh, soc + net * charge_efficiency)
        else:
            soc += net
            if soc < 0:
                unmet[i] = -soc
                soc = 0.0
        charge[i] = soc
    return charge, unmet


def data_path(site):
    return os.path.join(DATA_DIR, f"pvgis_{site}.csv.gz")


def load_site_raw(site):
    """Hourly data saved by get_solar_data.py: UTC time (YYYYMMDDHH), solar output per kWp (W), outdoor air (C)."""
    with gzip.open(data_path(site), "rt", encoding="ascii") as f:
        rows = [line.strip().split(",") for line in f if line and line[0].isdigit()]
    stamp = np.array([r[0] for r in rows])
    pv_per_kwp = np.array([float(r[1]) for r in rows])
    outdoor = np.array([float(r[2]) for r in rows])
    return stamp, pv_per_kwp, outdoor


def missing_hours(stamp, pv_per_kwp, max_zero_share=0.02):
    """Hours treated as gaps in the satellite record.

    An hour is missing if its output is exactly zero while that hour of the day, in that calendar
    month, is zero in under 2 percent of the record. Real weather almost never gives exactly zero
    at such hours (even heavy cloud lets some light through); genuinely dark hours, such as just
    after sunrise in some months, are zero far more often and are kept.
    """
    month = np.array([int(x[4:6]) for x in stamp])
    hour = np.array([int(x[8:10]) for x in stamp])
    zero = pv_per_kwp == 0.0
    missing = np.zeros(len(pv_per_kwp), dtype=bool)
    for m in range(1, 13):
        for h in range(24):
            sel = (month == m) & (hour == h)
            if sel.any() and zero[sel].mean() < max_zero_share:
                missing |= sel & zero
    return missing


def fill_missing(stamp, pv_per_kwp, missing):
    """Replace missing hours with the median output of the same month and hour in the rest of the record."""
    month = np.array([int(x[4:6]) for x in stamp])
    hour = np.array([int(x[8:10]) for x in stamp])
    out = pv_per_kwp.copy()
    for i in np.nonzero(missing)[0]:
        sel = (month == month[i]) & (hour == hour[i]) & ~missing
        out[i] = float(np.median(pv_per_kwp[sel]))
    return out


def longest_run(mask):
    best = run = 0
    for v in mask.tolist():
        run = run + 1 if v else 0
        best = max(best, run)
    return best


def load_site(site):
    """Hourly data with satellite gaps filled (see missing_hours)."""
    stamp, pv, outdoor = load_site_raw(site)
    return stamp, fill_missing(stamp, pv, missing_hours(stamp, pv)), outdoor


def years_and_months(stamp):
    years = np.array([int(s[:4]) for s in stamp])
    months = np.array([int(s[4:6]) for s in stamp])
    return years, months


def monthly_yield_kwh_per_kwp_day(stamp, pv_per_kwp):
    """Average daily solar output of a 1 kWp array for each calendar month (kWh per kWp per day)."""
    years, months = years_and_months(stamp)
    out = []
    for m in range(1, 13):
        sel = months == m
        days = sel.sum() / 24.0
        out.append(pv_per_kwp[sel].sum() / 1000.0 / days)
    return np.array(out)


def size_battery(pv_per_kwp, load_w, kwp, s: SolarSetup, usable_fraction):
    """Rated battery (Wh) for a solar array of kwp kWp that never runs empty over the whole record."""
    usable = usable_storage_needed_wh(pv_per_kwp * kwp, load_w, s.charge_efficiency)
    return usable / usable_fraction
