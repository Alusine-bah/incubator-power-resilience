"""Incubator power-failure model. Every parameter lives in Params."""
from dataclasses import dataclass
import numpy as np

# Incubator air temperature for the first 24 h of life by birth weight
# (UCSF Benioff Children's hospital manual, 2004). kg, deg C.
SETPOINT_TABLE = ((0.5, 35.5), (1.0, 34.9), (1.5, 34.0), (2.0, 33.5),
                  (2.5, 33.2), (3.0, 33.0), (3.5, 32.8), (4.0, 32.6))


def setpoint_for_weight(kg):
    w = [a for a, _ in SETPOINT_TABLE]
    t = [b for _, b in SETPOINT_TABLE]
    return float(np.interp(kg, w, t))


def skin_area_m2(kg):
    """Body surface area. Boyd weight-only table: 0.16 m2 at 2 kg; exponent 0.67 from Haycock 1978."""
    return 0.16 * (kg / 2.0) ** 0.67


@dataclass(frozen=True)
class Params:
    heater_w: float = 350.0          # about the 368 W maximum measured on a commercial incubator (one device)
    ua: float = 14.8                 # W/C, measured: 162.95 W / (36 - 25 C), one commercial incubator
    room_c: float = 22.0
    setpoint_override: float = 0.0   # 0 = use the published table for the baby's weight
    air_capacity: float = 20000.0    # J/C, assumption
    baby_mass_kg: float = 2.0
    baby_cp: float = 3500.0          # J/kg/C
    metabolic_w_per_kg: float = 2.0  # W/kg, from oxygen consumption of preterm infants
    baby_start_c: float = 37.0
    efficiency: float = 0.9
    usable_fraction: float = 0.8
    charger_w: float = 200.0         # W, assumption: a charger sized to refill the battery between outages
    trigger_drop_c: float = 0.6
    swing_c: float = 0.5

    @property
    def setpoint_c(self):
        if self.setpoint_override > 0:
            return self.setpoint_override
        return setpoint_for_weight(self.baby_mass_kg)

    @property
    def metabolic_w(self):
        return self.metabolic_w_per_kg * self.baby_mass_kg

    @property
    def ha(self):
        # heat loss coefficient baby to air, set so the baby balances at its start temperature
        return self.metabolic_w / (self.baby_start_c - self.setpoint_c)


LEGACY = dict(heater_w=300.0, ua=5.0, setpoint_override=33.5, metabolic_w_per_kg=1.5, charger_w=60.0)


def legacy_params(**changes):
    """The settings used for the first set of results (UA 5, 300 W heater, 3 W baby). Kept for regression tests."""
    return Params(**{**LEGACY, **changes})


def grid_profile(events, hours):
    v = np.ones(int(hours * 3600))
    for start_h, length_h, fraction in events:
        v[int(start_h * 3600):int((start_h + length_h) * 3600)] = fraction
    return v


def repeated_outages(length_h, days=2, starts=(4, 12, 20)):
    return [(24 * d + s, length_h, 0.0) for d in range(days) for s in starts]


def simulate(p, grid, rating_wh):
    n = len(grid)
    usable = p.usable_fraction * rating_wh
    soc = usable
    soc_min = soc
    sp = p.setpoint_c
    T = sp
    Tb = p.baby_start_c
    c_b = p.baby_mass_kg * p.baby_cp
    ha = p.ha
    metab = p.metabolic_w
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
        if T < sp - p.swing_c: heater_on = True
        if T > sp + p.swing_c: heater_on = False
        if T < sp - p.trigger_drop_c: latch = True
        if T > sp - p.trigger_drop_c + p.swing_c: latch = False
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
            else:
                empty_s += 1
        elif not under:
            soc = min(usable, soc + p.charger_w * p.efficiency / 3600.0)
        power = p.heater_w * v * v if heater_on else 0.0
        T += (power - p.ua * (T - p.room_c)) / p.air_capacity
        Tb += (metab - ha * (Tb - T)) / c_b
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
