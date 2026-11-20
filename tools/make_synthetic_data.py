"""Generate the synthetic NOKTA dataset used in the workshop.

The data imitate the NOKTA field protocol: three campuses, six fixed point
types per campus, two field rounds with the visiting order reversed in the
second round, one portable station per campus at about 1.5 m, 15-minute
visits sampled every 10 seconds, ten sensor channels, a field form for every
visit and a co-location test of the three stations. All values are invented
by this script. They are plausible for a sunny November morning at
mid-latitudes, but they describe no real campus.

Run:  python tools/make_synthetic_data.py
Writes the CSV files of the data/ folder. The seed is fixed, so every run
produces the same files.
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 2026
OUT = Path(__file__).resolve().parents[1] / "data"

# Point types, in the order of the first field round (P1 ... P6).
POINTS = [
    # id,  type,          dT,   dTd,  pm_add, coarse, co2_add, light, uv,  traffic, people, green, sun
    ("P1", "shaded",     -1.4, 0.0,   1.0,   0.0,    4.0,    0.12, 0.38,  2,   40,  5,  "shade"),
    ("P2", "traffic",     0.6, -0.1,  0.0,   6.0,    9.0,    0.85, 0.90, 95,   25,  5,  "partial"),
    ("P3", "reference",   0.0, 0.0,   0.0,   0.0,    0.0,    0.92, 0.95,  0,   10, 30,  "sun"),
    ("P4", "sunny_hard",  2.0, -0.3,  0.5,   5.0,    2.0,    1.08, 1.00, 10,   35,  0,  "sun"),
    ("P5", "crowded",     0.4, 0.0,   1.5,   1.5,   15.0,    0.70, 0.78,  5,  260, 10,  "partial"),
    ("P6", "green",      -1.0, 0.8,  -2.0,  -1.0,   -6.0,    0.45, 0.55,  0,   20, 85,  "partial"),
]

CAMPUSES = {
    #      station, pressure base,  temperatures R1/R2,  dew points R1/R2,  pm bg R1/R2,  co2 bg R1/R2, lux max R1/R2
    "A": dict(station="S1", p=(902.5, 897.0), t=(11.5, 9.0), td=(1.0, 2.5),
              pm=(16.0, 9.0), co2=(436.0, 428.0), lux=(62000, 52000), scale=1.00,
              date=("2026-11-11", "2026-11-18"), sky=("clear", "partly cloudy")),
    "B": dict(station="S2", p=(913.0, 909.5), t=(8.5, 7.0), td=(-2.0, -0.5),
              pm=(19.0, 12.0), co2=(441.0, 433.0), lux=(60000, 50000), scale=1.10,
              date=("2026-11-12", "2026-11-19"), sky=("clear", "partly cloudy")),
    "C": dict(station="S3", p=(1017.5, 1012.0), t=(18.0, 15.5), td=(9.0, 12.0),
              pm=(9.0, 8.0), co2=(431.0, 429.0), lux=(65000, 48000), scale=0.90,
              date=("2026-11-10", "2026-11-17"), sky=("clear", "humid, hazy")),
}

# Station offsets found in the co-location test (S1 is the reference unit).
STATION = {
    "S1": dict(dT=0.0, dRH=0.0, pm_gain=1.00, dCO2=0.0),
    "S2": dict(dT=0.6, dRH=-2.0, pm_gain=1.00, dCO2=12.0),
    "S3": dict(dT=-0.2, dRH=0.0, pm_gain=1.15, dCO2=-8.0),
}

KAPPA = 0.3          # bulk hygroscopicity used by the PM humidity artefact
RHO_P = 1.65         # dry particle density, g/cm3
DT = 10              # seconds between samples
VISIT_MIN = 15       # minutes recorded at each point
STEP_MIN = 25        # minutes between the starts of two visits
WARMUP_S = 120       # first two minutes after a move are a settling period
LUX_MAX = 65535      # a 16-bit light sensor cannot report more


def magnus_rh(t, td):
    """Relative humidity (%) from temperature and dew point (deg C)."""
    a, b = 17.625, 243.04
    return 100.0 * np.exp(a * td / (b + td) - a * t / (b + t))


def hygro_factor(rh):
    """Mass growth of particles with humidity (Crilley et al., 2018, Eq. 5)."""
    aw = np.clip(rh, 1.0, 99.0) / 100.0
    return 1.0 + (KAPPA / RHO_P) / (-1.0 + 1.0 / aw)


def solar_shape(hour):
    """Smooth daylight shape that peaks at 11:50 local time."""
    return np.clip(np.cos((hour - 11.83) / 6.2 * np.pi / 2) ** 1.6, 0, 1)


def plumes(rng, n, rate_per_min, peak, tau_s):
    """Sum of decaying plumes from random events (vehicles, smokers)."""
    out = np.zeros(n)
    k = rng.poisson(rate_per_min * n * DT / 60.0)
    for _ in range(k):
        start = rng.integers(0, n)
        height = rng.uniform(*peak)
        tau = rng.uniform(*tau_s) / DT
        idx = np.arange(start, n)
        out[idx] += height * np.exp(-(idx - start) / tau)
    return out


def clouds(rng, n, n_events):
    """Multiplicative dimming of light and UV by passing clouds."""
    f = np.ones(n)
    for _ in range(n_events):
        start = rng.integers(0, n)
        length = rng.integers(3, 10)
        depth = rng.uniform(0.35, 0.70)
        f[start:start + length] *= depth
    return f


def make_visits(rng):
    rows, truth, forms = [], [], []
    sample_id = 0
    for c, cfg in CAMPUSES.items():
        st = STATION[cfg["station"]]
        for r in (1, 2):
            order = POINTS if r == 1 else POINTS[::-1]
            date = cfg["date"][r - 1]
            prev = dict(t=21.0, rh=38.0, co2=650.0)   # carried from indoors
            for k, pt in enumerate(order):
                (pid, ptype, dT, dTd, pm_add, coarse, co2_add, light, uv,
                 traffic, people, green, sun) = pt
                start_min = 10 * 60 + STEP_MIN * k
                n = VISIT_MIN * 60 // DT
                sec = np.arange(n) * DT
                hour = (start_min + sec / 60.0) / 60.0
                s = cfg["scale"]
                # --- background drivers of the morning ---------------------
                t_bg = cfg["t"][r - 1] + 1.8 * (hour - 10) - 0.15 * (hour - 10) ** 2
                td_bg = cfg["td"][r - 1] - 0.25 * (hour - 10)
                p_bg = cfg["p"][r - 1] - 0.6 * (hour - 10)
                pm_bg = cfg["pm"][r - 1] * (1 - 0.13 * (hour - 10))
                co2_bg = cfg["co2"][r - 1] - 6.0 * (hour - 10)
                sky = solar_shape(hour) * cfg["lux"][r - 1]
                cl = clouds(rng, n, 0 if r == 1 else 4)
                # --- true values at the point -----------------------------
                sun_f = {"sun": 1.0, "partial": 0.6, "shade": 0.0}[sun]
                rad_err = 1.5 * sun_f * solar_shape(hour) * (cl ** 0.5)
                t_true = (t_bg + s * dT + rad_err * (ptype == "sunny_hard")
                          + rng.normal(0, 0.08, n).cumsum() * 0.15)
                td_true = td_bg + dTd + rng.normal(0, 0.06, n)
                td_true = np.minimum(td_true, t_true - 0.3)
                rh_true = magnus_rh(t_true, td_true)
                veh_rate = traffic / 15.0 * (1.15 if r == 1 else 0.85)
                pm_plume = plumes(rng, n, veh_rate * 0.25, (4, 18), (15, 40))
                smoke = (plumes(rng, n, 0.45, (25, 110), (8, 20))
                         if ptype == "crowded" else np.zeros(n))
                pm25 = np.maximum(
                    pm_bg + s * pm_add + pm_plume * s + smoke
                    + rng.lognormal(0, 0.18, n) - 1.0, 1.0)
                pm1 = pm25 * rng.normal(0.78, 0.02, n) - 0.15 * smoke
                pm10 = (pm25 * rng.normal(1.32, 0.04, n) + s * max(coarse, 0)
                        + 0.25 * pm_plume + 0.4 * coarse * rng.random(n))
                co2_plume = plumes(rng, n, veh_rate * 0.25, (8, 40), (10, 25))
                co2 = (co2_bg + s * co2_add + co2_plume
                       + (rng.normal(0, 6, n) if ptype == "crowded" else 0)
                       + rng.normal(0, 3.0, n))
                lux = sky * light * cl * rng.normal(1, 0.015, n)
                if ptype == "green":
                    lux *= rng.uniform(0.6, 1.25, n)          # dappled shade
                uva = sky * 0.00042 * uv * cl * rng.normal(1, 0.02, n)
                uvb = uva * 0.016 * rng.normal(1, 0.03, n)
                pres = p_bg + rng.normal(0, 0.06, n)
                # --- sensor response --------------------------------------
                lab = np.array(["ok"] * n, dtype=object)
                w = sec < WARMUP_S
                lag_t = (prev["t"] - t_true[0]) * np.exp(-sec / 45.0)
                lag_rh = (prev["rh"] - rh_true[0]) * np.exp(-sec / 55.0)
                lag_c = (prev["co2"] - co2[0]) * np.exp(-sec / 30.0)
                t_raw = t_true + lag_t + st["dT"] + rng.normal(0, 0.05, n)
                rh_raw = np.clip(rh_true + lag_rh + st["dRH"]
                                 + rng.normal(0, 0.4, n), 5, 99.5)
                co2_raw = co2 + lag_c + st["dCO2"]
                g = hygro_factor(rh_true) * st["pm_gain"]
                pm1_raw, pm25_raw, pm10_raw = pm1 * g, pm25 * g, pm10 * g
                lux_raw = lux.copy()
                lab[w] = "warmup"
                # saturation of the light sensor
                sat = lux_raw >= LUX_MAX
                lux_raw[sat] = LUX_MAX
                lab[sat & ~w] = "saturated"
                # humid episode
                hum = rh_true > 85
                lab[hum & (lab == "ok")] = "high_rh"
                # single-sample glitches
                if rng.random() < 0.85:
                    for _ in range(rng.integers(1, 3)):
                        i = rng.integers(14, n)
                        ch = rng.choice(["pm10", "pm25", "co2"])
                        if ch == "pm10":
                            pm10_raw[i] = rng.choice([999.9, pm10_raw[i] * 6])
                        elif ch == "pm25":
                            pm25_raw[i] = pm25_raw[i] * rng.uniform(5, 9)
                        else:
                            co2_raw[i] = rng.choice([2000.0, 0.0])
                        lab[i] = "spike_" + ch
                # stuck CO2 sensor on one visit
                if c == "B" and r == 1 and pid == "P1":
                    co2_raw[30:54] = 452.0
                    lab[30:54] = "flatline_co2"
                # logging dropouts
                cols_nan = []
                if c == "A" and r == 2 and pid == "P5":
                    cols_nan = [(slice(40, 46), "all")]
                if c == "C" and r == 1 and pid == "P2":
                    cols_nan = [(slice(60, 63), "pm")]
                frame = pd.DataFrame({
                    "timestamp": [f"{date} {int(m // 60):02d}:{int(m % 60):02d}:"
                                  f"{int(round((m * 60) % 60)):02d}"
                                  for m in start_min + sec / 60.0],
                    "campus": c, "round": r, "point_id": pid, "point_type": ptype,
                    "visit_order": k + 1, "station": cfg["station"],
                    "seconds_since_arrival": sec,
                    "temperature_c": t_raw.round(2),
                    "rel_humidity_pct": rh_raw.round(1),
                    "pressure_hpa": pres.round(2),
                    "pm1_ugm3": np.maximum(pm1_raw, 0.5).round(1),
                    "pm25_ugm3": np.maximum(pm25_raw, 0.5).round(1),
                    "pm10_ugm3": np.maximum(pm10_raw, 0.5).round(1),
                    "co2_ppm": co2_raw.round(0),
                    "light_lux": lux_raw.round(0),
                    "uva_wm2": uva.round(2),
                    "uvb_wm2": uvb.round(3),
                })
                for sl, what in cols_nan:
                    if what == "all":
                        frame.loc[frame.index[sl], "temperature_c":"uvb_wm2"] = np.nan
                    else:
                        frame.loc[frame.index[sl],
                                  ["pm1_ugm3", "pm25_ugm3", "pm10_ugm3"]] = np.nan
                    lab[sl] = "gap"
                frame.insert(0, "sample_id", np.arange(sample_id, sample_id + n))
                truth.append(pd.DataFrame({"sample_id": frame["sample_id"],
                                           "qc_truth": lab}))
                sample_id += n
                rows.append(frame)
                note = {
                    "shaded": "Narrow passage between two buildings, no direct sun.",
                    "traffic": "Two meters from the campus road; buses stop nearby.",
                    "reference": "Open lawn edge away from roads and entrances.",
                    "sunny_hard": "Concrete square in full sun; station housing "
                                  "in direct sun.",
                    "crowded": "Faculty entrance; a group was smoking near the door.",
                    "green": "Under a row of trees; grass irrigated in the morning.",
                }[ptype]
                if k == 0:
                    note += " First stop: the station was brought from indoors."
                if c == "B" and r == 1 and pid == "P1":
                    note += " CO2 reading looked frozen for a few minutes."
                if c == "A" and r == 2 and pid == "P5":
                    note += " Logger restarted once."
                forms.append(dict(
                    campus=c, round=r, point_id=pid, point_type=ptype,
                    visit_order=k + 1, date=date,
                    start=f"{start_min // 60:02d}:{start_min % 60:02d}",
                    end=f"{(start_min + VISIT_MIN) // 60:02d}:"
                        f"{(start_min + VISIT_MIN) % 60:02d}",
                    vehicles_15min=int(rng.poisson(traffic * (1.15 if r == 1 else 0.85))),
                    people_15min=int(rng.poisson(people)),
                    sun_condition=sun, sky=cfg["sky"][r - 1],
                    green_cover_pct=green, station=cfg["station"],
                    notes=note))
                prev = dict(t=t_true[-1], rh=rh_true[-1], co2=co2[-1])
    return (pd.concat(rows, ignore_index=True), pd.concat(truth, ignore_index=True),
            pd.DataFrame(forms))


def make_colocation(rng):
    """Two hours with the three stations side by side, one reading per minute."""
    minutes = np.arange(120)
    t = 16.0 + 1.2 * np.sin(minutes / 120 * np.pi) + rng.normal(0, 0.05, 120).cumsum() * 0.1
    rh = 52.0 - 2.0 * np.sin(minutes / 120 * np.pi) + rng.normal(0, 0.3, 120)
    pm = 12.0 + 4.0 * np.sin(minutes / 37.0) ** 2 + rng.lognormal(0, 0.15, 120)
    co2 = 445.0 + 8.0 * np.cos(minutes / 50.0) + rng.normal(0, 2.0, 120)
    rows = []
    for s, off in STATION.items():
        rows.append(pd.DataFrame({
            "timestamp": [f"2026-10-31 {14 + m // 60:02d}:{m % 60:02d}:00" for m in minutes],
            "station": s,
            "temperature_c": (t + off["dT"] + rng.normal(0, 0.06, 120)).round(2),
            "rel_humidity_pct": (rh + off["dRH"] + rng.normal(0, 0.4, 120)).round(1),
            "pm25_ugm3": (pm * off["pm_gain"] * rng.normal(1, 0.04, 120)).round(1),
            "co2_ppm": (co2 + off["dCO2"] + rng.normal(0, 3.0, 120)).round(0),
        }))
    return pd.concat(rows, ignore_index=True)


def main():
    rng = np.random.default_rng(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    data, truth, forms = make_visits(rng)
    coloc = make_colocation(rng)
    data.to_csv(OUT / "nokta_synthetic.csv", index=False)
    truth.to_csv(OUT / "nokta_synthetic_qc_truth.csv", index=False)
    forms.to_csv(OUT / "nokta_field_forms_synthetic.csv", index=False)
    coloc.to_csv(OUT / "nokta_colocation_synthetic.csv", index=False)
    data.head(0).to_csv(OUT / "nokta_template.csv", index=False)
    print(len(data), "readings,", len(forms), "visits,", len(coloc), "co-location rows")
    print(truth["qc_truth"].value_counts().to_string())


if __name__ == "__main__":
    main()
