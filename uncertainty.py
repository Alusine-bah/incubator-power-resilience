"""Uncertainty analysis: vary the inputs across their published ranges and see how sure the conclusions are."""
import os
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from model import Params, grid_profile, simulate

SEED = 2026
N = 2000
N_WEIGHT = 500
BIG = 1000000.0
D = "\u00b0C"

# Input ranges. "chosen" = our judgement, centred on or spanning the published values (see PARAMETERS.md).
RANGES = {
    "heat_loss": "triangular 10 / 14.8 / 20 W per C (chosen, centred on the one measurement)",
    "baby_heat": "uniform 1.9 to 2.8 W per kg (oxygen consumption and energy expenditure studies)",
    "room": "uniform 20 to 30 C (datasheet operating range)",
    "heat_stored": "uniform 5 to 30 kJ per C (assumption)",
    "heater": "uniform 300 to 400 W (around the 368 W measured maximum)",
    "efficiency": "uniform 0.80 to 0.95 (inverter datasheet and idle draw)",
    "outage_hours": "lognormal, median 1.5 h, sigma 0.9, limited to 0.25 to 11 h (chosen to span the published ranges)",
    "grid_voltage": "uniform 0.55 to 0.90 of nominal (Sierra Leone sensor data)",
}


def draw(rng, n):
    return {
        "heat_loss": rng.triangular(10.0, 14.8, 20.0, n),
        "baby_heat": rng.uniform(1.9, 2.8, n),
        "room": rng.uniform(20.0, 30.0, n),
        "heat_stored": rng.uniform(5.0, 30.0, n),
        "heater": rng.uniform(300.0, 400.0, n),
        "efficiency": rng.uniform(0.80, 0.95, n),
        "outage_hours": np.clip(rng.lognormal(np.log(1.5), 0.9, n), 0.25, 11.0),
        "grid_voltage": rng.uniform(0.55, 0.90, n),
    }


def make_params(heater, ua, room, stored, baby_heat, eff, kg):
    return Params(heater_w=heater, ua=ua, room_c=room, air_capacity=stored * 1000.0, baby_mass_kg=kg,
                  metabolic_w_per_kg=baby_heat, efficiency=eff)


def needed_rating(p, grid):
    r = simulate(p, grid, BIG)
    return (p.usable_fraction * BIG - r["lowest_charge_wh"]) / p.usable_fraction


def one_case(job):
    heater, ua, room, stored, baby_heat, eff, volt, kg, light = job
    p = make_params(heater, ua, room, stored, baby_heat, eff, kg)
    blackout3 = grid_profile([(0.5, 3.0, 0.0)], 4.0)
    if light:
        return (needed_rating(p, blackout3) / 3.0, 0.0, 0.0, 0.0)
    blackout2 = grid_profile([(0.5, 2.0, 0.0)], 3.5)
    brown = grid_profile([(0.5, 6.0, volt)], 7.0)
    return (
        needed_rating(p, blackout3) / 3.0,                 # rated battery per outage hour
        simulate(p, blackout2, 0)["lowest_core"],          # no backup, 2 h blackout
        needed_rating(p, brown),                           # rated battery for 6 h low voltage
        simulate(p, brown, 0)["lowest_core"],              # no backup, 6 h low voltage
    )


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def run(s, kg, workers, light=False):
    jobs = [(float(s["heater"][i]), float(s["heat_loss"][i]), float(s["room"][i]), float(s["heat_stored"][i]),
             float(s["baby_heat"][i]), float(s["efficiency"][i]), float(s["grid_voltage"][i]), kg, light)
            for i in range(len(s["heat_loss"]))]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        out = list(ex.map(one_case, jobs, chunksize=10))
    return np.array(out)


CASES_FILE = "docs/uncertainty_cases.csv"
CASE_COLUMNS = ("heat_loss", "baby_heat", "room", "heat_stored", "heater", "efficiency", "outage_hours", "grid_voltage")


def save_cases(s, res, path=CASES_FILE):
    """One row per random case: its inputs and results, for the dashboard."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write(",".join(CASE_COLUMNS) + ",battery_per_outage_hour_wh,lowest_core_2h_no_backup_c,battery_6h_low_voltage_wh\n")
        for i in range(len(s["heat_loss"])):
            vals = [s[k][i] for k in CASE_COLUMNS] + [res[i, 0], res[i, 1], res[i, 2]]
            f.write(",".join(f"{v:.4f}" for v in vals) + "\n")


def main():
    t0 = time.time()
    workers = max(1, (os.cpu_count() or 2) - 1)
    rng = np.random.default_rng(SEED)
    s = draw(rng, N)
    res = run(s, 2.0, workers)
    per_hour, cold2, brown_need, cold6 = res.T
    save_cases(s, res)

    print("Inputs varied (all other inputs at their defaults; 2 kg baby):")
    for k, v in RANGES.items():
        print(f"  {k}: {v}")
    print()
    print(f"{N} random cases, seed {SEED}.")
    print()
    print("1. Rated battery needed per outage hour (80 percent usable), 2 kg baby")
    q = np.percentile(per_hour, [5, 25, 50, 75, 95])
    print(f"   5th {q[0]:.0f}, 25th {q[1]:.0f}, median {q[2]:.0f}, 75th {q[3]:.0f}, 95th {q[4]:.0f} Wh per hour")
    print()
    print("2. Share of outages a given battery covers (outage length drawn from the chosen distribution)")
    need = per_hour * s["outage_hours"]
    ratings = (250, 500, 750, 1000, 1500, 2000)
    cover = {r: float(np.mean(need <= r)) for r in ratings}
    for r in ratings:
        print(f"   {r:5d} Wh covers {100 * cover[r]:.0f}% of cases")
    for pct in (50, 90, 95):
        print(f"   battery covering {pct}% of cases: {np.percentile(need, pct):.0f} Wh")
    print()
    print("3. No backup, 2 h blackout, 2 kg baby: lowest core temperature")
    print(f"   median {np.median(cold2):.1f} C, 5th to 95th percentile {np.percentile(cold2, 5):.1f} to {np.percentile(cold2, 95):.1f} C")
    print(f"   below 32 C in {100 * np.mean(cold2 < 32.0):.0f}% of cases; below 36.5 C in {100 * np.mean(cold2 < 36.5):.0f}%")
    print()
    print("4. Grid at 0.55 to 0.90 of nominal for 6 h, 2 kg baby")
    print(f"   no battery needed in {100 * np.mean(brown_need < 1.0):.0f}% of cases")
    needy = brown_need[brown_need >= 1.0]
    print(f"   when needed, rated battery median {np.median(needy):.0f} Wh, 95th percentile {np.percentile(needy, 95):.0f} Wh")
    print(f"   no backup: core below 36.5 C in {100 * np.mean(cold6 < 36.5):.0f}% of cases; below 32 C in {100 * np.mean(cold6 < 32.0):.0f}%")
    print()
    print("5. Which inputs matter (Spearman rank correlation; closer to 1 or -1 means stronger)")
    names = [("heat_loss", "heat loss"), ("room", "room temperature"), ("efficiency", "converter efficiency"),
             ("baby_heat", "baby heat production"), ("heat_stored", "heat stored in incubator"), ("heater", "heater power")]
    sens_need = {nm: spearman(s[k], per_hour) for k, nm in names}
    sens_cold = {nm: spearman(s[k], cold2) for k, nm in names}
    print("   battery per outage hour:", ", ".join(f"{k} {v:+.2f}" for k, v in sens_need.items()))
    print("   no-backup lowest temperature (2 h):", ", ".join(f"{k} {v:+.2f}" for k, v in sens_cold.items()))
    print()
    print(f"6. Median rated battery per outage hour by birth weight ({N_WEIGHT} cases each)")
    for kg in (0.5, 1.0, 2.0, 3.0, 4.0):
        s2 = draw(np.random.default_rng(SEED + 1), N_WEIGHT)
        r2 = run(s2, kg, workers, light=True)
        print(f"   {kg} kg: median {np.median(r2[:, 0]):.0f} Wh per hour (5th to 95th: {np.percentile(r2[:, 0], 5):.0f} to {np.percentile(r2[:, 0], 95):.0f})")

    print()
    print("7. Rated battery per outage hour by room temperature (measured heat loss 14.8, 2 kg baby, default incubator)")
    for rc in (20, 22, 25, 28, 30):
        pr = replace(Params(), room_c=float(rc))
        print(f"   room {rc} C: {needed_rating(pr, grid_profile([(0.5, 3.0, 0.0)], 4.0)) / 3.0:.0f} Wh per outage hour")

    os.makedirs("docs", exist_ok=True)
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
    ax[0].hist(per_hour, bins=40, color="tab:blue")
    for v, lab in zip(q[[0, 2, 4]], ("5th", "median", "95th")):
        ax[0].axvline(v, color="black", ls=":")
        ax[0].text(v, ax[0].get_ylim()[1] * 0.92, lab, rotation=90, ha="right", fontsize=8)
    ax[0].set_xlabel("Rated battery per outage hour (Wh)")
    ax[0].set_ylabel("Number of cases")
    ax[0].set_title("Battery needed per hour of blackout")
    xs = np.linspace(0, 3000, 300)
    ax[1].plot(xs, [100 * np.mean(need <= x) for x in xs], color="tab:green")
    ax[1].set_xlabel("Rated battery (Wh)")
    ax[1].set_ylabel("Share of cases covered (%)")
    ax[1].set_title("Coverage (depends on the chosen outage lengths)")
    ax[1].grid(alpha=0.3)
    labels = [nm for _, nm in names]
    y = np.arange(len(labels))
    ax[2].barh(y - 0.2, [sens_need[l] for l in labels], height=0.4, label="battery per hour")
    ax[2].barh(y + 0.2, [sens_cold[l] for l in labels], height=0.4, label="no-backup temperature")
    ax[2].set_yticks(y)
    ax[2].set_yticklabels(labels)
    ax[2].axvline(0, color="black", lw=0.8)
    ax[2].set_xlabel("Rank correlation")
    ax[2].set_title("Which inputs matter")
    ax[2].legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)
    fig.tight_layout()
    fig.savefig("docs/uncertainty.png", dpi=130)
    print()
    print(f"Saved docs/uncertainty.png ({time.time() - t0:.0f} s, {workers} workers)")


if __name__ == "__main__":
    main()
