import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from model import Params, grid_profile, simulate

D = "\u00b0C"
p = Params()
grid = grid_profile([(0.5, 2.0, 0.0)], 6.5)
with_b = simulate(p, grid, 500)
without = simulate(p, grid, 0)
step = 30
t = np.arange(len(grid))[::step] / 3600.0

fig, ax = plt.subplots(4, 1, sharex=True, figsize=(8, 9))
ax[0].plot(t, grid[::step] * 230.0, color="black")
ax[0].set_ylabel("Grid (V)")
ax[0].set_title("2 h blackout: baby with and without a 500 Wh backup battery")
ax[1].plot(t, with_b["air"][::step], label="with backup")
ax[1].plot(t, without["air"][::step], "--", label="no backup")
ax[1].axhline(33.5, color="gray", ls=":")
ax[1].set_ylabel("Incubator air (" + D + ")")
ax[1].legend()
ax[2].plot(t, with_b["core"][::step], color="tab:red", label="with backup")
ax[2].plot(t, without["core"][::step], "--", color="tab:orange", label="no backup")
ax[2].axhline(36.5, color="gray", ls=":")
ax[2].set_ylabel("Baby core (" + D + ")")
ax[2].legend()
ax[3].plot(t, with_b["charge"][::step], color="tab:green")
ax[3].set_ylabel("Battery (Wh)")
ax[3].set_xlabel("Time (hours)")
fig.tight_layout()
os.makedirs("docs", exist_ok=True)
fig.savefig("docs/blackout_example.png", dpi=130)
print("Saved docs/blackout_example.png")

