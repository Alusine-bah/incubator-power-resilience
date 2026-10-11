"""Incubator power-failure model. Every parameter lives in Params."""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Params:
    heater_w: float = 300.0        # rated heater power at full voltage (W)
    ua: float = 5.0                # heat loss, incubator to room (W/C)
    room_c: float = 22.0
    setpoint_c: float = 33.5
    air_capacity: float = 20000.0  # incubator thermal capacity (J/C), assumption
    baby_mass_kg: float = 2.0
    baby_cp: float = 3500.0        # J/kg/C
    metabolic_w: float = 3.0
    baby_start_c: float = 37.0
    efficiency: float = 0.9        # battery converter efficiency
    usable_fraction: float = 0.8   # share of rated battery capacity that is usable
    charger_w: float = 60.0        # assumption
    trigger_drop_c: float = 0.6    # feedback trigger below setpoint
    swing_c: float = 0.5           # thermostat swing either side of setpoint

    @property
    def ha(self):
        # heat loss coefficient baby to air, set so the baby balances at start temperature
        return self.metabolic_w / (self.baby_start_c - self.setpoint_c)


def grid_profile(events, hours):
    """events: list of (start_hour, length_hours, voltage_fraction). 1.0 = normal."""
    v = np.ones(int(hours * 3600))
    for start_h, length_h, fraction in events:
        v[int(start_h * 3600):int((start_h + length_h) * 3600)] = fraction
    return v


def repeated_outages(length_h, days=2, starts=(4, 12, 20)):
    return [(24 * d + s, length_h, 0.0) for d in range(days) for s in starts]


def simulate(p, grid, rating_wh):
    """One step per second. grid = voltage fraction per second."""
    n = len(grid)
    usable = p.usable_fraction * rating_wh
    soc = usable
    soc_min = soc
    T = p.setpoint_c
    Tb = p.baby_start_c
    c_b = p.baby_mass_kg * p.baby_cp
    heater_on = True
    latch = False
    used = 0.0
    empty_s = 0
    below_s = 0
    air = np.empty(n)
    core = np.empty(n)
    charge = np.empty(n)
    for i in range(n):
        vg = grid[i]
        if T < p.setpoint_c - p.swing_c: heater_on = True
        if T > p.setpoint_c + p.swing_c: heater_on = False
        if T < p.setpoint_c - p.trigger_drop_c: latch = True
        if T > p.setpoint_c - p.trigger_drop_c + p.swing_c: latch = False
        v = vg
        failed = vg < 0.05
        under = vg < 1.0
        if under and (failed or latch):
            if soc > 0:
                v = 1.0
                if heater_on:
                    e = min(p.heater_w / p.efficiency / 3600.0, soc)
                    soc -= e
                    used += e
            elif failed:
                empty_s += 1
        elif not under:
            soc = min(usable, soc + p.charger_w * p.efficiency / 3600.0)
        power = p.heater_w * v * v if heater_on else 0.0
        T += (power - p.ua * (T - p.room_c)) / p.air_capacity
        Tb += (p.metabolic_w - p.ha * (Tb - T)) / c_b
        soc_min = min(soc_min, soc)
        if Tb < 36.5: below_s += 1
        air[i] = T
        core[i] = Tb
        charge[i] = soc
    return {
        "air": air, "core": core, "charge": charge,
        "lowest_air": air.min(), "lowest_core": core.min(),
        "minutes_core_below_36_5": below_s / 60.0,
        "minutes_battery_empty": empty_s / 60.0,
        "battery_used_wh": used, "lowest_charge_wh": soc_min,
    }
