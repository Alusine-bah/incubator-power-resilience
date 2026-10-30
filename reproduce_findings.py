"""Re-run every number quoted in README.md through model.py and compare."""
import sys
import time
from dataclasses import replace
from model import Params, legacy_params, grid_profile, repeated_outages, simulate

BIG = 1000000.0
bad = []
start = time.time()


def check(name, readme, got, tol):
    ok = abs(got - readme) <= tol
    if not ok:
        bad.append(name)
    print(f"{'OK  ' if ok else 'DIFF'} | {name}: README {readme:g}, model {got:.2f}")


def needed(p, grid):
    r = simulate(p, grid, BIG)
    return (p.usable_fraction * BIG - r["lowest_charge_wh"]) / p.usable_fraction, r


def blackout(h):
    return grid_profile([(0.5, h, 0.0)], 0.5 + h + 4)


def brownout(v, h=6.0):
    return grid_profile([(0.5, h, v)], 0.5 + h + 4)


d = Params()

print("--- Default incubator, 2 kg baby, 22 C room: blackouts ---")
for hours, want in ((2, 475), (3, 712), (8, 1895), (11, 2607)):
    n, r = needed(d, blackout(hours))
    check(f"{hours} h blackout: battery rating (Wh)", want, n, max(10, 0.02 * want))
    check(f"{hours} h blackout: lowest baby temperature with backup (C)", 37.0, r["lowest_core"], 0.05)
    check(f"{hours} h blackout: battery energy per hour (Wh)", 190, r["battery_used_wh"] / hours, 5)
n0 = simulate(d, blackout(2), 0)
check("2 h blackout, no backup: lowest baby temperature (C)", 29.9, n0["lowest_core"], 0.15)

print()
print("--- By birth weight, 2 h blackout ---")
for kg, want, want_core in ((0.5, 561, 25.2), (1.0, 531, 26.9), (2.0, 475, 29.9), (3.0, 454, 30.7), (4.0, 436, 31.3)):
    q = Params(baby_mass_kg=kg)
    n, r = needed(q, blackout(2))
    check(f"{kg} kg: battery rating (Wh)", want, n, 10)
    check(f"{kg} kg: no backup, lowest baby temperature (C)", want_core, simulate(q, blackout(2), 0)["lowest_core"], 0.2)

print()
print("--- Heat loss sensitivity, 2 h blackout, 2 kg baby ---")
for ua, want in ((5, 158), (8, 256), (11, 350), (14.8, 475), (20, 642)):
    n, _ = needed(replace(d, ua=float(ua)), blackout(2))
    check(f"heat loss {ua} W/C: battery rating (Wh)", want, n, 10)

print()
print("--- Low voltage for 6 h ---")
for v in (0.7, 0.75, 0.8, 0.9):
    n, _ = needed(d, brownout(v))
    check(f"grid at {v} of nominal: battery rating (Wh)", 0, n, 5)
for v, want, want_core, want_min in ((0.6, 508, 34.1, 506), (0.55, 706, 32.8, 553)):
    n, _ = needed(d, brownout(v))
    check(f"grid at {v} of nominal: battery rating (Wh)", want, n, 15)
    nb = simulate(d, brownout(v), 0)
    check(f"grid at {v}, no backup: lowest baby temperature (C)", want_core, nb["lowest_core"], 0.15)
    check(f"grid at {v}, no backup: minutes below 36.5 C", want_min, nb["minutes_core_below_36_5"], 10)
loss = d.ua * (d.setpoint_c - d.room_c)
check("lowest grid voltage the heater holds alone (fraction of nominal)", 0.70, (loss / d.heater_w) ** 0.5, 0.02)

print()
print("--- Charger, three blackouts a day for 2 days ---")
for ch, h, want in ((60, 2.0, 814), (100, 2.0, 476), (200, 2.0, 476), (60, 3.0, 2566), (200, 3.0, 713)):
    n, _ = needed(replace(d, charger_w=float(ch)), grid_profile(repeated_outages(h), 48))
    check(f"{h} h blackouts, {ch} W charger: battery rating (Wh)", want, n, max(10, 0.03 * want))

print()
print("--- Heater warm-up and measured heat loss ---")
T, t = 22.0, 0
while T < 35.0 and t < 36000:
    T += (d.heater_w - d.ua * (T - 22.0)) / d.air_capacity
    t += 1
check("warm-up from 22 to 35 C (minutes)", 18.0, t / 60.0, 0.3)
check("heat loss x 11 C = measured heat power (W)", 162.95, d.ua * 11.0, 0.5)

print()
print(f"({time.time() - start:.0f} s)")
print("Everything reproduced." if not bad else f"{len(bad)} differ: " + "; ".join(bad))
sys.exit(1 if bad else 0)
