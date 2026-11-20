"""Compute every number shown on the workshop pages and write site-data.js.

The pages run in the browser without a server, so their data travel in one
JavaScript file. This script uses the same functions, settings and seeds as
the Colab notebooks (tools/nokta_core.py), so a number met on a page
reappears in the notebook.

Run:  python tools/build_site_data.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import partial_dependence, permutation_importance
from sklearn.metrics import r2_score, silhouette_score
from sklearn.model_selection import KFold, LeaveOneGroupOut, cross_val_predict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from nokta_core import (CHANNELS, CLUSTER_FEATURES, MODEL_FEATURES, PM,  # noqa: E402
                        RANDOM_STATE, add_anomalies, apply_offsets,
                        clean_readings, colocation_offsets, correct_pm,
                        dew_point, fair_table, flag_quality, forest_predict_dicts,
                        humidity_factor, load_readings, minute_table, model_table,
                        pearson_r, robust_z, spike_scores, standardize,
                        tree_to_dict, visit_table)

DATA = ROOT / "data"


def r(x, nd=2):
    """Round floats for compact JSON; keep None for missing values."""
    if isinstance(x, (list, tuple, np.ndarray, pd.Series)):
        return [r(v, nd) for v in list(x)]
    if x is None:
        return None
    try:
        xf = float(x)
    except (TypeError, ValueError):
        return x
    if not np.isfinite(xf):
        return None
    return round(xf, nd)


def main():
    df = load_readings(DATA / "nokta_synthetic.csv")
    truth = pd.read_csv(DATA / "nokta_synthetic_qc_truth.csv")
    forms = pd.read_csv(DATA / "nokta_field_forms_synthetic.csv")
    coloc = pd.read_csv(DATA / "nokta_colocation_synthetic.csv")

    flags = flag_quality(df)
    clean = clean_readings(df, flags)
    offsets = colocation_offsets(coloc)
    adj_raw = apply_offsets(clean, offsets)
    adj = correct_pm(adj_raw)
    minutes = minute_table(adj)
    minutes_raw_pm = minute_table(adj_raw)
    visits = visit_table(minutes)
    out = {}

    # ------------------------------------------------------------ twin
    twin = {}
    show = ["temperature_c", "rel_humidity_pct", "pressure_hpa", "pm1_ugm3",
            "pm25_ugm3", "pm10_ugm3", "co2_ppm", "light_lux", "uva_wm2", "uvb_wm2"]
    for (c, rd), g in minutes.groupby(["campus", "round"]):
        vs = []
        for (pid, ptype, order), gv in g.groupby(["point_id", "point_type", "visit_order"]):
            form = forms[(forms.campus == c) & (forms["round"] == rd)
                         & (forms.point_id == pid)].iloc[0]
            vs.append(dict(
                pid=pid, type=ptype, order=int(order), start=form["start"],
                end=form["end"], vehicles=int(form["vehicles_15min"]),
                people=int(form["people_15min"]), sun=form["sun_condition"],
                minutes=gv["minute"].astype(int).tolist(),
                series={ch: r(gv[ch], 1 if ch != "uvb_wm2" else 3) for ch in show},
                median={ch: r(gv[ch].median(), 2 if ch != "uvb_wm2" else 3)
                        for ch in show}))
        vs.sort(key=lambda v: v["order"])
        twin.setdefault(c, {})[str(rd)] = vs
    out["twin"] = twin

    # ------------------------------------------------------------ fair tables
    fair = {}
    for ch in ["temperature_c", "pm25_ugm3", "co2_ppm", "rel_humidity_pct",
               "light_lux", "pm10_ugm3", "uva_wm2"]:
        ft = fair_table(visits, ch)
        fair[ch] = [dict(campus=row.campus, type=row.point_type, r1=r(row.round1),
                         r2=r(row.round2), mean=r(row.two_round_mean),
                         ref=r(row.minus_reference)) for row in ft.itertuples()]
    out["fair"] = fair
    vt = visits.copy()
    out["visit_hours"] = {f"{a}-{b}-{c}": r(h, 3) for a, b, c, h in
                          vt[["campus", "round", "point_type", "hour"]].itertuples(index=False)}

    # ------------------------------------------------------------ quality control
    lab = truth["qc_truth"].to_numpy()
    qc = {}
    for vid in ["B-R1-P1", "C-R2-P6", "A-R1-P2", "B-R1-P5"]:
        g = df[df.visit == vid]
        idx = g.index
        z = {ch: r(df.loc[idx, ch].pipe(lambda s: spike_scores(s)), 2)
             for ch in ["pm25_ugm3", "pm10_ugm3", "co2_ppm"]}
        qc[vid] = dict(
            sec=g["seconds_since_arrival"].astype(int).tolist(),
            raw={ch: r(g[ch], 2) for ch in CHANNELS},
            truth=lab[idx].tolist(),
            z=z,
            flags={k: flags.loc[idx, k].astype(int).tolist() for k in flags.columns})
    rows = []
    pairs = [("warmup", "warmup"), ("spike_pm25", "spike_pm25_ugm3"),
             ("spike_pm10", "spike_pm10_ugm3"), ("spike_co2", "spike_co2_ppm"),
             ("flatline_co2", "flatline_co2"), ("gap", "gap"),
             ("saturated", "saturated_light"), ("high_rh", "high_rh")]
    for name, col in pairs:
        f = flags[col].to_numpy()
        rows.append(dict(problem=name, planted=int((lab == name).sum()),
                         flagged=int(f.sum()), caught=int(((lab == name) & f).sum())))
    out["qc"] = dict(visits=qc, score=rows, n=int(len(df)))
    # missing is not zero: a small worked example from one dropout
    gap = df[df.visit == "A-R2-P5"]["temperature_c"].iloc[30:52]
    out["qc"]["gap_example"] = dict(values=r(gap, 2),
                                    mean_skip=r(gap.mean(), 2),
                                    mean_zero=r(gap.fillna(0).mean(), 2))

    # ------------------------------------------------------------ co-location
    wide = {ch: coloc.pivot(index="timestamp", columns="station", values=ch)
            for ch in ["temperature_c", "pm25_ugm3", "co2_ppm"]}
    out["coloc"] = dict(
        minutes=list(range(len(wide["temperature_c"]))),
        series={ch: {s: r(wide[ch][s], 2) for s in ["S1", "S2", "S3"]} for ch in wide},
        offsets={s: dict(t=r(offsets.loc[s, "temperature_c"], 2),
                         rh=r(offsets.loc[s, "rel_humidity_pct"], 2),
                         co2=r(offsets.loc[s, "co2_ppm"], 1),
                         pm=r(offsets.loc[s, "pm_ratio"], 3))
                 for s in offsets.index})

    # ------------------------------------------------------------ humidity factor
    rh_grid = np.arange(30, 96, 1)
    out["humidity"] = dict(rh=rh_grid.tolist(), c=r(humidity_factor(rh_grid), 3))
    hum = minutes_raw_pm[(minutes_raw_pm.campus == "C") & (minutes_raw_pm["round"] == 2)]
    hum_c = minutes[(minutes.campus == "C") & (minutes["round"] == 2)]
    out["humidity"]["campusC_round2"] = [
        dict(type=t, raw=r(g1["pm25_ugm3"].median()),
             corrected=r(hum_c[hum_c.point_type == t]["pm25_ugm3"].median()),
             rh=r(g1["rel_humidity_pct"].median(), 1))
        for t, g1 in hum.groupby("point_type")]

    # ------------------------------------------------------------ box plots
    m = add_anomalies(minutes)
    box = {}
    for ch in ["temp_anomaly", "pm25_anomaly", "co2_anomaly", "log10_lux"]:
        box[ch] = {}
        for t, g in m.groupby("point_type"):
            v = g[ch].dropna().to_numpy()
            q1, q2, q3 = np.percentile(v, [25, 50, 75])
            iqr = q3 - q1
            lo = v[v >= q1 - 1.5 * iqr].min()
            hi = v[v <= q3 + 1.5 * iqr].max()
            box[ch][t] = dict(q1=r(q1), med=r(q2), q3=r(q3), lo=r(lo), hi=r(hi),
                              mean=r(v.mean()), n=int(len(v)),
                              out=r(v[(v < lo) | (v > hi)], 2))
    out["box"] = box

    # ------------------------------------------------------------ correlation
    within = {}
    for (c, rd), g in minutes.groupby(["campus", "round"]):
        within[f"{c}{rd}"] = r(pearson_r(g.temperature_c, g.pressure_hpa), 3)
    out["corr"] = dict(
        pts=[[r(a, 2), r(b, 2), c, int(d), t] for a, b, c, d, t in
             minutes[["temperature_c", "pressure_hpa", "campus", "round",
                      "point_type"]].itertuples(index=False)],
        pooled=r(pearson_r(minutes.temperature_c, minutes.pressure_hpa), 3),
        within=within)
    dp = minutes.assign(dew=dew_point(minutes.temperature_c, minutes.rel_humidity_pct))
    out["dew"] = {f"{c}{rd}": {t: r(g[g.point_type == t]["dew"].median(), 1)
                               for t in g.point_type.unique()}
                  for (c, rd), g in dp.groupby(["campus", "round"])}

    # ------------------------------------------------------------ clustering
    X = m[CLUSTER_FEATURES].to_numpy()
    Z, mu, sd = standardize(X)
    clus = dict(raw=[r(row, 2) for row in X], z=[r(row, 3) for row in Z],
                type=m.point_type.tolist(), campus=m.campus.tolist(),
                round=m["round"].astype(int).tolist(), mu=r(mu, 4), sd=r(sd, 4),
                labels={}, centers={}, inertia={}, silhouette={})
    for k in range(2, 7):
        km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit(Z)
        # order clusters by temperature anomaly of the center for stable colors
        order = np.argsort(km.cluster_centers_[:, 0])
        remap = {old: new for new, old in enumerate(order)}
        clus["labels"][k] = [remap[l] for l in km.labels_]
        clus["centers"][k] = [r(km.cluster_centers_[o], 3) for o in order]
        clus["inertia"][k] = r(km.inertia_, 1)
        clus["silhouette"][k] = r(silhouette_score(Z, km.labels_), 3)
    feats = ["temp_anomaly", "rel_humidity_pct", "pm25_anomaly", "co2_anomaly",
             "log10_lux", "uva_wm2"]
    mm = m.copy()
    mm["co2_anomaly"] = mm["co2_anomaly"].fillna(0.0)   # a missing minute sits at the median
    Zp, _, _ = standardize(mm[feats].to_numpy())
    pca = PCA(n_components=3, random_state=RANDOM_STATE).fit(Zp)
    S = pca.transform(Zp)
    clus["pca"] = dict(features=feats, var=r(pca.explained_variance_ratio_, 3),
                       loadings=[r(v, 3) for v in pca.components_],
                       scores=[r(row, 3) for row in S],
                       type=mm.point_type.tolist())
    out["cluster"] = clus

    # ------------------------------------------------------------ explainable model
    t = model_table(minutes, forms).dropna(subset=MODEL_FEATURES + ["pm25_ugm3"])
    Xm = t[MODEL_FEATURES].to_numpy()
    y = t["pm25_ugm3"].to_numpy()
    groups = (t.campus + t.point_id).to_numpy()
    rf = RandomForestRegressor(n_estimators=40, max_depth=6, min_samples_leaf=5,
                               random_state=RANDOM_STATE, n_jobs=-1)
    p_rand = cross_val_predict(rf, Xm, y, cv=KFold(5, shuffle=True,
                                                   random_state=RANDOM_STATE))
    p_group = cross_val_predict(rf, Xm, y, cv=LeaveOneGroupOut(), groups=groups)
    rf.fit(Xm, y)
    r2_train = r2_score(y, rf.predict(Xm))
    imps = []
    for c in ["A", "B", "C"]:
        tr = (t.campus != c).to_numpy()
        rf_c = RandomForestRegressor(n_estimators=40, max_depth=6, min_samples_leaf=5,
                                     random_state=RANDOM_STATE, n_jobs=-1)
        rf_c.fit(Xm[tr], y[tr])
        pi = permutation_importance(rf_c, Xm[~tr], y[~tr], n_repeats=10,
                                    random_state=RANDOM_STATE)
        imps.append(pi.importances_mean)
    imp = np.mean(imps, axis=0)
    trees = [tree_to_dict(e) for e in rf.estimators_]
    js_pred = forest_predict_dicts(trees, Xm[:50])
    assert np.allclose(js_pred, rf.predict(Xm[:50]), atol=1e-3), "export mismatch"
    pdp = {}
    for fname in ["vehicles_per_min", "background_pm25", "people_per_min",
                  "green_cover_pct"]:
        j = MODEL_FEATURES.index(fname)
        res = partial_dependence(rf, Xm, [j], grid_resolution=25)
        pdp[fname] = dict(x=r(res["grid_values"][0], 3), y=r(res["average"][0], 3))
    out["rf"] = dict(
        features=MODEL_FEATURES, trees=trees,
        median=r(np.median(Xm, axis=0), 3), min=r(Xm.min(axis=0), 3),
        max=r(Xm.max(axis=0), 3),
        cv=dict(train=r(r2_train, 3), random=r(r2_score(y, p_rand), 3),
                group=r(r2_score(y, p_group), 3), n=int(len(y)),
                groups=int(len(set(groups)))),
        importance=r(imp, 4), pdp=pdp)

    # ------------------------------------------------------------ fact sheets
    facts = {}
    for c in ["A", "B", "C"]:
        rows_c = []
        for ch in ["pm25_ugm3", "temperature_c", "co2_ppm", "rel_humidity_pct",
                   "light_lux"]:
            for row in fair_table(visits, ch).query("campus == @c").itertuples():
                rows_c.append(dict(channel=ch, type=row.point_type,
                                   r1=r(row.round1, 1), r2=r(row.round2, 1),
                                   mean=r(row.two_round_mean, 1),
                                   ref=r(row.minus_reference, 1)))
        facts[c] = rows_c
    out["facts"] = facts
    out["counts"] = dict(readings=int(len(df)), visits=int(len(forms)),
                         minutes=int(len(minutes)))

    js = "window.NOKTA = " + json.dumps(out, separators=(",", ":")) + ";\n"
    target = ROOT / "docs" / "assets" / "site-data.js"
    target.write_text(js, encoding="utf-8")
    (ROOT / "tools" / "site_summary.json").write_text(json.dumps(dict(
        cv=out["rf"]["cv"], importance=dict(zip(MODEL_FEATURES, out["rf"]["importance"])),
        qc=rows, offsets=out["coloc"]["offsets"],
        silhouette=out["cluster"]["silhouette"], inertia=out["cluster"]["inertia"],
        pca_var=out["cluster"]["pca"]["var"], corr=dict(pooled=out["corr"]["pooled"],
                                                        within=within),
        humidity=out["humidity"]["campusC_round2"],
        gap=out["qc"]["gap_example"]), indent=1), encoding="utf-8")
    print(f"site-data.js: {target.stat().st_size / 1024:.0f} kB")


if __name__ == "__main__":
    main()
