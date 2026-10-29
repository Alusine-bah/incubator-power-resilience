from dataclasses import replace
from model import Params, legacy_params, grid_profile, repeated_outages, simulate

BIG = 1000000
bad = []


def check(name, readme, got, tol):
    ok = abs(got - readme) <= tol
    if not ok:
        bad.append(name)
    print(f"{'OK  ' if ok else 'DIFF'} | {name}: README {readme:g}, model {got:.2f}")


def check_range(name, lo, hi, got):
    ok = lo <= got <= hi
    if not ok:
        bad.append(name)
    print(f"{'OK  ' if ok else 'DIFF'} | {name}: README {lo:g} to {hi:g}, model {got:.2f}")


def brownout(heater, ua, v, hours=6.0):
    p = replace(legacy_params(), heater_w=float(heater), ua=float(ua))
    g = grid_profile([(0.5, hours, v)], 0.5 + hours + 4)
    return simulate(p, g, BIG)


print("--- Sustained undervoltage, 6 h ---")
for ua in (5, 8):
    for v in (0.55, 0.6, 0.7, 0.85):
        r = brownout(300, ua, v)
        check(f"300 W, UA {ua}, {v} pu: battery Wh", 0, r["battery_used_wh"], 1.0)
r = brownout(300, 8, 0.55)
check("300 W, UA 8, 0.55 pu: lowest core", 36.84, r["lowest_core"], 0.03)
for v in (0.55, 0.6, 0.7, 0.85):
    r = brownout(200, 5, v)
    check(f"200 W, UA 5, {v} pu: battery Wh", 0, r["battery_used_wh"], 1.0)
r = brownout(200, 8, 0.6)
check("200 W, UA 8, 0.6 pu: battery Wh", 180, r["battery_used_wh"], 4.0)
check("200 W, UA 8, 0.6 pu: lowest core", 36.67, r["lowest_core"], 0.03)
r = brownout(200, 8, 0.55)
check("200 W, UA 8, 0.55 pu: battery Wh", 275, r["battery_used_wh"], 5.0)
check("200 W, UA 8, 0.55 pu: lowest core", 36.67, r["lowest_core"], 0.03)

print()
print("--- Blackout energy, UA 5, room 22 C, immediate transfer to battery ---")
for hours in (1.5, 2.0, 3.0, 8.0, 11.0):
    g = grid_profile([(0.5, hours, 0.0)], 0.5 + hours + 4)
    r = simulate(legacy_params(), g, BIG)
    wh = r["battery_used_wh"]
    print(f"INFO | {hours} h blackout: battery {wh:.0f} Wh = {wh / hours:.1f} Wh per hour, "
          f"rating at 80% usable {wh / 0.8:.0f} Wh, lowest core {r['lowest_core']:.2f}")
    if hours >= 1.5:
        check(f"{hours} h blackout: Wh per hour (UA x temperature difference / efficiency)", 63.9, wh / hours, 3.0)

print()
print("--- No backup, 2 h blackout ---")
for cap_kj, want in ((5, 30.90), (10, 31.68), (20, 32.98), (30, 33.60)):
    pp = replace(legacy_params(), air_capacity=cap_kj * 1000.0)
    g = grid_profile([(0.5, 2.0, 0.0)], 6.5)
    r = simulate(pp, g, 0)
    check(f"C = {cap_kj} kJ/C: lowest core", want, r["lowest_core"], 0.1)

print()
print("--- Repeated blackouts, 3 a day for 48 h ---")
cases = [(1.5, 100, 87, 36.82), (1.5, 150, 0, 36.99), (3.0, 100, 639, 33.33),
         (3.0, 150, 397, 35.10), (3.0, 200, 197, 36.40), (3.0, 300, 0, 36.99)]
for length, rating, empty, core in cases:
    r = simulate(legacy_params(), grid_profile(repeated_outages(length), 48), rating)
    check(f"{length} h, {rating} Wh: minutes battery empty", empty, r["minutes_battery_empty"], max(5, 0.03 * empty))
    check(f"{length} h, {rating} Wh: lowest core", core, r["lowest_core"], 0.1)


def warmup(heater, ua=5.0, c=20000.0, room=22.0):
    T, t = room, 0
    while T < 35.0 and t < 36000:
        T += (heater - ua * (T - room)) / c
        t += 1
    return t / 60.0


print()
print("--- Warm-up from 22 to 35 C ---")
for w, want in ((200, 26.2), (250, 20.1), (300, 16.3), (400, 11.8)):
    check(f"{w} W heater: minutes", want, warmup(w), 0.2)

print()
print("Everything reproduced." if not bad else f"{len(bad)} differ: " + "; ".join(bad))


