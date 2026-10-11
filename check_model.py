from dataclasses import replace
from model import Params, grid_profile, repeated_outages, simulate


def check(name, got, want, tol):
    ok = abs(got - want) <= tol
    print(f"{'PASS' if ok else 'FAIL'} | {name}: got {got:.2f}, earlier result {want:.2f} (tolerance {tol})")
    return ok


p = Params()
results = []

grid = grid_profile(repeated_outages(3.0), 48)
r = simulate(p, grid, 300)
results.append(check("3 h outages, 300 Wh: lowest charge (Wh)", r["lowest_charge_wh"], 47.9, 2.0))
results.append(check("3 h outages, 300 Wh: lowest core (C)", r["lowest_core"], 36.99, 0.03))

r = simulate(p, grid, 200)
results.append(check("3 h outages, 200 Wh: minutes battery empty", r["minutes_battery_empty"], 197, 5))
results.append(check("3 h outages, 200 Wh: lowest core (C)", r["lowest_core"], 36.40, 0.05))

p2 = replace(p, heater_w=200.0, ua=8.0)
grid2 = grid_profile([(0.5, 6.0, 0.6)], 10.5)
r = simulate(p2, grid2, 1000000)
results.append(check("200 W, UA 8, 6 h at 0.6 pu: battery used (Wh)", r["battery_used_wh"], 179.8, 3.0))
results.append(check("200 W, UA 8, 6 h at 0.6 pu: lowest core (C)", r["lowest_core"], 36.67, 0.03))

print()
print("All checks passed." if all(results) else "Some checks failed. Paste this output here.")
