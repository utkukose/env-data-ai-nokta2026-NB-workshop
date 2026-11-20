"""Analysis functions shared by the Colab notebooks and the site data builder.

The notebooks contain the same functions as code cells, so participants can
read and change them. tools/build_site_data.py imports this module to compute
every number shown on the workshop pages with the same code and seeds.
"""
import re
import numpy as np
import pandas as pd

RANDOM_STATE = 2026

CHANNELS = ["temperature_c", "rel_humidity_pct", "pressure_hpa", "pm1_ugm3",
            "pm25_ugm3", "pm10_ugm3", "co2_ppm", "light_lux", "uva_wm2",
            "uvb_wm2"]
PM = ["pm1_ugm3", "pm25_ugm3", "pm10_ugm3"]
POINT_TYPES = ["shaded", "traffic", "reference", "sunny_hard", "crowded", "green"]
LUX_MAX = 65535


# ---------------------------------------------------------------- loading
def load_readings(path):
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df["visit"] = (df["campus"] + "-R" + df["round"].astype(str) + "-"
                   + df["point_id"])
    return df


# ------------------------------------------------------- quality control
def robust_z(x):
    """Modified z-score: 0.6745 (x - median) / MAD (Leys et al., 2013)."""
    x = np.asarray(x, dtype=float)
    med = np.nanmedian(x)
    mad = np.nanmedian(np.abs(x - med))
    if not np.isfinite(mad) or mad == 0:
        return np.zeros_like(x)
    return 0.6745 * (x - med) / mad


def spike_scores(series, window=5):
    """Robust z-score of the distance from a running median."""
    run_med = series.rolling(window, center=True, min_periods=1).median()
    return pd.Series(robust_z(series - run_med), index=series.index)


def flag_quality(df, z_limit=6.0, warmup_s=120, flat_len=12):
    """Return one boolean column per quality problem (raw data are kept)."""
    f = pd.DataFrame(index=df.index)
    f["warmup"] = df["seconds_since_arrival"] < warmup_s
    f["gap"] = df[CHANNELS].isna().any(axis=1)
    f["saturated_light"] = df["light_lux"] >= LUX_MAX
    f["high_rh"] = df["rel_humidity_pct"] > 85
    jump = {}
    for ch in PM:
        z = df.groupby("visit")[ch].transform(spike_scores)
        run_med = df.groupby("visit")[ch].transform(
            lambda s: s.rolling(5, center=True, min_periods=1).median())
        jump[ch] = (z.abs() > z_limit) & (df[ch] > 2 * run_med)
    jump = pd.DataFrame(jump)
    for ch in PM:
        # a real plume lifts every particle size, a glitch lifts only one
        f["spike_" + ch] = jump[ch] & ~jump.drop(columns=ch).any(axis=1)
    f["spike_co2_ppm"] = (df["co2_ppm"] <= 300) | (df["co2_ppm"] >= 2000)
    roll_sd = df.groupby("visit")["co2_ppm"].transform(
        lambda s: s.rolling(flat_len, min_periods=flat_len).std())
    end_of_run = (roll_sd == 0).astype(int)
    # spread the flag back over the whole frozen window
    spread = end_of_run[::-1].groupby(df["visit"][::-1]).transform(
        lambda s: s.rolling(flat_len, min_periods=1).max())[::-1]
    f["flatline_co2"] = spread.fillna(0).astype(bool)
    return f


def clean_readings(df, flags):
    """Copy of the data with flagged values set to missing (never to zero)."""
    out = df.copy()
    out.loc[flags["warmup"], CHANNELS] = np.nan
    out.loc[flags["saturated_light"], "light_lux"] = np.nan
    out.loc[flags["flatline_co2"] | flags["spike_co2_ppm"], "co2_ppm"] = np.nan
    for ch in PM:
        out.loc[flags["spike_" + ch], ch] = np.nan
    return out


def colocation_offsets(coloc):
    """Offset of each station from the mean of the three stations."""
    wide = {ch: coloc.pivot(index="timestamp", columns="station", values=ch)
            for ch in ["temperature_c", "rel_humidity_pct", "pm25_ugm3", "co2_ppm"]}
    rows = []
    for s in sorted(coloc["station"].unique()):
        rows.append(dict(
            station=s,
            temperature_c=(wide["temperature_c"][s]
                           - wide["temperature_c"].mean(axis=1)).mean(),
            rel_humidity_pct=(wide["rel_humidity_pct"][s]
                              - wide["rel_humidity_pct"].mean(axis=1)).mean(),
            co2_ppm=(wide["co2_ppm"][s] - wide["co2_ppm"].mean(axis=1)).mean(),
            pm_ratio=(wide["pm25_ugm3"][s] / wide["pm25_ugm3"].mean(axis=1)).mean(),
        ))
    return pd.DataFrame(rows).set_index("station")


def apply_offsets(df, offsets):
    out = df.copy()
    st = out["station"]
    for ch in ["temperature_c", "rel_humidity_pct", "co2_ppm"]:
        out[ch] = out[ch] - st.map(offsets[ch])
    for ch in PM:
        out[ch] = out[ch] / st.map(offsets["pm_ratio"])
    return out


def humidity_factor(rh, kappa=0.3, rho_p=1.65):
    """Growth factor C of particle mass with humidity (Crilley et al., 2018)."""
    aw = np.clip(np.asarray(rh, dtype=float), 1, 99) / 100.0
    return 1.0 + (kappa / rho_p) / (-1.0 + 1.0 / aw)


def correct_pm(df):
    out = df.copy()
    c = humidity_factor(out["rel_humidity_pct"])
    for ch in PM:
        out[ch] = out[ch] / c
    return out


def minute_table(df):
    """Median of every channel for each minute of each visit."""
    d = df.copy()
    d["minute"] = d["seconds_since_arrival"] // 60
    keys = ["campus", "round", "point_id", "point_type", "visit_order",
            "station", "visit", "minute"]
    m = d.groupby(keys)[CHANNELS].median().reset_index()
    t0 = d.groupby(keys)["timestamp"].min().reset_index(drop=True)
    m["hour"] = t0.dt.hour + t0.dt.minute / 60.0
    return m.dropna(subset=["temperature_c"]).reset_index(drop=True)


# ------------------------------------------------ fair comparisons
def dew_point(t, rh):
    """Dew point (deg C) from the Magnus form (Alduchov & Eskridge, 1996)."""
    a, b = 17.625, 243.04
    g = np.log(np.asarray(rh, dtype=float) / 100.0) + a * t / (b + t)
    return b * g / (a - g)


def visit_table(minutes):
    keys = ["campus", "round", "point_id", "point_type", "visit_order"]
    v = minutes.groupby(keys)[CHANNELS + ["hour"]].median().reset_index()
    return v


def fair_table(visits, channel):
    """Round 1, Round 2, their mean and the difference from the reference."""
    w = visits.pivot_table(index=["campus", "point_type"], columns="round",
                           values=channel).rename(columns={1: "round1", 2: "round2"})
    w["two_round_mean"] = (w["round1"] + w["round2"]) / 2
    ref = w.xs("reference", level="point_type")["two_round_mean"]
    w["minus_reference"] = w["two_round_mean"] - ref.reindex(
        w.index.get_level_values("campus")).values
    return w.reset_index()


def pearson_r(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    return float(np.corrcoef(x[ok], y[ok])[0, 1])


# ------------------------------------------------ unsupervised AI
CLUSTER_FEATURES = ["temp_anomaly", "log10_lux", "pm25_anomaly"]


def add_anomalies(minutes):
    m = minutes.copy()
    grp = m.groupby(["campus", "round"])
    m["temp_anomaly"] = m["temperature_c"] - grp["temperature_c"].transform("median")
    m["pm25_anomaly"] = m["pm25_ugm3"] - grp["pm25_ugm3"].transform("median")
    m["co2_anomaly"] = m["co2_ppm"] - grp["co2_ppm"].transform("median")
    m["log10_lux"] = np.log10(m["light_lux"].fillna(LUX_MAX))
    return m


def standardize(X):
    mu, sd = X.mean(axis=0), X.std(axis=0, ddof=0)
    return (X - mu) / sd, mu, sd


# ------------------------------------------------ explainable model
MODEL_FEATURES = ["vehicles_per_min", "people_per_min", "green_cover_pct",
                  "sun_index", "rel_humidity_pct", "temperature_c", "hour",
                  "background_pm25"]


def model_table(minutes, forms, target_minutes=None):
    m = minutes.merge(
        forms[["campus", "round", "point_id", "vehicles_15min", "people_15min",
               "green_cover_pct", "sun_condition"]],
        on=["campus", "round", "point_id"], how="left")
    m["vehicles_per_min"] = m["vehicles_15min"] / 15.0
    m["people_per_min"] = m["people_15min"] / 15.0
    m["sun_index"] = m["sun_condition"].map({"shade": 0.0, "partial": 0.5,
                                             "sun": 1.0})
    ref = (m[m["point_type"] == "reference"]
           .groupby(["campus", "round"])["pm25_ugm3"].median()
           .rename("background_pm25"))
    m = m.merge(ref, on=["campus", "round"], how="left")
    return m


def tree_to_dict(est):
    t = est.tree_
    return dict(f=t.feature.tolist(), t=np.round(t.threshold, 6).tolist(),
                l=t.children_left.tolist(), r=t.children_right.tolist(),
                v=np.round(t.value[:, 0, 0], 5).tolist())


def forest_predict_dicts(trees, X):
    out = np.zeros(len(X))
    for tr in trees:
        for i, row in enumerate(X):
            n = 0
            while tr["l"][n] != -1:
                n = tr["l"][n] if row[tr["f"][n]] <= tr["t"][n] else tr["r"][n]
            out[i] += tr["v"][n]
    return out / len(trees)


# ------------------------------------------------ from numbers to words
NUMBER = re.compile(r"(?<![\w.,])-?\d+(?:[.,]\d+)?")


def audit_numbers(text, facts, tol=0.051):
    """List every number of a text and whether the fact table supports it."""
    allowed = []
    for v in np.ravel(facts.select_dtypes("number").to_numpy()):
        if np.isfinite(v):
            allowed.append(float(v))
    rows = []
    for m in NUMBER.finditer(text):
        val = float(m.group().replace(",", "."))
        hit = any(abs(val - a) <= tol for a in allowed)
        rows.append(dict(number=m.group(), supported=hit,
                         context=text[max(0, m.start() - 30):m.end() + 30]))
    return pd.DataFrame(rows)
