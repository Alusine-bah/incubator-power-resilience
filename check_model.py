from dataclasses import replace
from model import (Params, legacy_params, grid_profile, repeated_outages, simulate,
                   setpoint_for_weight, skin_area_m2)

results = []


def check(name, got, want, tol):
    ok = abs(got - want) <= tol
    print(f"{'PASS' if ok else 'FAIL'} | {name}: got {got:.2f}, expected {want:.2f} (tolerance {tol})")
    results.append(ok)


def check_between(name, got, lo, hi):
    ok = lo <= got <= hi
    print(f"{'PASS' if ok else 'FAIL'} | {name}: got {got:.3f}, allowed {lo:.3f} to {hi:.3f}")
    results.append(ok)


def needed_rating(p, grid):
    big = 1000000.0
    r = simulate(p, grid, big)
    return (p.usable_fraction * big - r["lowest_charge_wh"]) / p.usable_fraction


print("--- Regression: first results, legacy settings (UA 5, 300 W, 3 W baby, 60 W charger) ---")
p = legacy_params()
grid = grid_profile(repeated_outages(3.0), 48)
r = simulate(p, grid, 300)
check("3 h outages, 300 Wh: lowest charge (Wh)", r["lowest_charge_wh"], 47.9, 2.0)
check("3 h outages, 300 Wh: lowest core (C)", r["lowest_core"], 36.99, 0.03)
r = simulate(p, grid, 200)
check("3 h outages, 200 Wh: minutes battery empty", r["minutes_battery_empty"], 197, 5)
check("3 h outages, 200 Wh: lowest core (C)", r["lowest_core"], 36.40, 0.05)
p2 = replace(p, heater_w=200.0, ua=8.0)
r = simulate(p2, grid_profile([(0.5, 6.0, 0.6)], 10.5), 1000000)
check("200 W, UA 8, 6 h at 0.6: battery used (Wh)", r["battery_used_wh"], 179.8, 3.0)
check("200 W, UA 8, 6 h at 0.6: lowest core (C)", r["lowest_core"], 36.67, 0.03)

print()
print("--- Current defaults (measured heat loss, 2 kg baby) ---")
d = Params()
check("heat loss x (36 - 25) = measured 162.95 W", d.ua * 11.0, 162.95, 0.5)
check("setpoint at 0.5 kg (C)", setpoint_for_weight(0.5), 35.5, 0.01)
check("setpoint at 2.0 kg (C)", setpoint_for_weight(2.0), 33.5, 0.01)
check("setpoint at 1.75 kg, interpolated (C)", setpoint_for_weight(1.75), 33.75, 0.01)
g = grid_profile([(0.5, 2.0, 0.0)], 6.5)
a = simulate(d, g, 1000000)
n = simulate(d, g, 0)
check("2 h blackout: battery used (Wh)", a["battery_used_wh"], 380.4, 5.0)
check("2 h blackout with backup: lowest core (C)", a["lowest_core"], 37.0, 0.05)
check("2 h blackout, no backup: lowest core (C)", n["lowest_core"], 29.91, 0.15)
T, t = 22.0, 0
while T < 35.0 and t < 36000:
    T += (d.heater_w - d.ua * (T - 22.0)) / d.air_capacity
    t += 1
check("warm-up 22 to 35 C (minutes)", t / 60.0, 17.97, 0.3)

print()
print("--- Charger and low-voltage behaviour ---")
rep = grid_profile(repeated_outages(2.0), 48)
check("repeated 2 h blackouts, 200 W charger: battery rating needed (Wh)", needed_rating(d, rep), 476, 10)
check("repeated 2 h blackouts, 60 W charger: battery rating needed (Wh)", needed_rating(replace(d, charger_w=60.0), rep), 814, 20)
small = Params(baby_mass_kg=0.5)
r = simulate(small, grid_profile([(0.5, 6.0, 0.6)], 10.5), 500)
check("0.5 kg, 6 h at 0.6, 500 Wh: minutes battery empty", r["minutes_battery_empty"], 160, 8)

print()
print("--- Baby heat loss vs published coefficients (7 to 9.8 W/m2/C times surface area, 15 percent allowance) ---")
for kg in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0):
    q = Params(baby_mass_kg=kg)
    area = skin_area_m2(kg)
    check_between(f"{kg} kg: calibrated hA (W/C)", q.ha, 7.0 * area * 0.85, 9.8 * area * 1.15)

print()
print("--- Solar sizing (solar.py): hourly load and battery maths ---")
import numpy as np
from solar import SolarSetup, battery_side_load_w, usable_storage_needed_wh, run_hourly
for label, q in (("2 kg, room 22", Params()), ("0.5 kg, room 22", Params(baby_mass_kg=0.5)),
                 ("2 kg, room 28", Params(room_c=28.0))):
    r = simulate(q, grid_profile([(0.5, 8.0, 0.0)], 9.0), 1000000)
    per_hour = (r["charge"][int(3.5 * 3600)] - r["charge"][int(7.5 * 3600)]) / 4.0
    check(f"{label}: hourly load matches the second-by-second model (W)",
          float(battery_side_load_w(q, q.room_c)), per_hour, round(per_hour * 0.01, 1))
pv = np.array([0, 0, 300, 300, 0, 0], dtype=float)
need = usable_storage_needed_wh(pv, 100.0, 0.5)
check("battery maths: 2 dark hours, 2 sunny hours (+100 Wh stored each), 2 dark hours (Wh)", need, 200.0, 0.01)
charge, unmet = run_hourly(pv, 100.0, need, 0.5)
check("battery maths: that battery never runs empty (Wh unmet)", float(unmet.sum()), 0.0, 0.001)
charge, unmet = run_hourly(pv, 100.0, need - 50.0, 0.5)
check("battery maths: 50 Wh smaller runs 50 Wh short in each of the two dark spells", float(unmet.sum()), 100.0, 0.01)
from solar import missing_hours, fill_missing
st = np.array([f"2020{m:02d}{d:02d}{h:02d}" for m in (1,) for d in range(1, 29) for h in range(24)])
day = np.arange(len(st)) // 24
pvt = np.tile(np.array([0.0] * 7 + [400.0] * 10 + [0.0] * 7), 28)
pvt[(np.arange(len(st)) % 24) == 7] = 0.0                    # an hour that is always dark: real
pvt[day == 6] = 30.0                                           # a very dull day: real
pvt[(day == 9) & (np.arange(len(st)) % 24 >= 12)] = 0.0       # half a day of zeros: missing
m = missing_hours(st, pvt, max_zero_share=0.05)
check("data gaps: only the 5 zero daytime hours of the half-day gap are flagged", float(m.sum()), 5.0, 0.0)
check("data gaps: filled with the typical output for that hour (W)", float(fill_missing(st, pvt, m)[m].mean()), 400.0, 0.01)
from solar import grid_gains, outage_fraction, storage_from_gains
print()
print("--- Grid with outages plus solar (solar.py) ---")
for ch, want in ((200.0, 476.0), (60.0, 814.0)):
    o = np.zeros(48)
    for a, l, _ in repeated_outages(2.0):
        o[int(a):int(a + l)] = 1.0
    hourly = storage_from_gains(grid_gains(np.zeros(48), battery_side_load_w(d, d.room_c), o, ch, d.efficiency, 0.95)) / 0.8
    check(f"repeated 2 h blackouts, {ch:.0f} W charger, no solar: hourly battery matches the detailed model (Wh)",
          hourly, want, round(want * 0.02))
o = outage_fraction(87648, 2.0, 1.5, seed=2026)
check_between("random outages, 2 a day, median 1.5 h: hours a day without grid power", o.sum() / (87648 / 24.0), 3.0, 5.0)
check("random outages are repeatable (same seed, same outages)", float(np.abs(o - outage_fraction(87648, 2.0, 1.5, seed=2026)).sum()), 0.0, 0.0)
print()
print("All checks passed." if all(results) else "Some checks failed. Paste this output here.")
