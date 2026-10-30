"""Collect every number quoted in the revised paper into paper_rev/numbers.json.
Run from repo root after rev_sobol_convergence.py, rev_analysis.py and rev_aliasing.py."""
import json
import numpy as np, pandas as pd

out = {}
names9 = ["rugi_DC", "galat_GHI", "model_inverter", "transposisi", "model_suhu_sel", "dekomposisi_GHI",
          "NOCT", "geser_waktu", "pemetaan"]

# ---- Sobol, N = 4096 and convergence
for tag, key in [("rev05", "05"), ("rev10", "10")]:
    C = pd.read_csv(f"outputs/{tag}_conv.csv")
    s7 = C[C.seed == 7]
    last = s7[s7.N == s7.N.max()].set_index("factor")
    out["sobol" + key] = {f: dict(S1=float(last.loc[f, "S1"]), ST=float(last.loc[f, "ST"]), ST_conf=float(last.loc[f, "ST_conf"]))
                          for f in names9}
    a = s7[s7.N == 1024].set_index("factor").ST; b = last.ST
    out["conv_maxdiff" + key] = float((a - b).abs().max())
    seeds = C[C.N == 1024].groupby("factor").ST.std()
    out["seed_sd" + key] = float(seeds.max())
    out["interaction" + key] = float(last.ST.sum() - last.S1.sum())
    final_top = list(b.sort_values(ascending=False).index[:5])
    stable = int(s7.N.max())
    for n in sorted(s7.N.unique(), reverse=True):
        top = list(s7[s7.N == n].set_index("factor").ST.sort_values(ascending=False).index[:5])
        if top == final_top:
            stable = int(n)
        else:
            break
    out["rank_stable_from" + key] = stable
    if key == "05":
        nmax = int(s7.N.max()); D = 9
        E = np.load(f"outputs/{tag}_conv_E.npy")
        out["sobol_runs"] = int(len(E))
        idx = np.r_[np.arange(0, len(E), D + 2), np.arange(D + 1, len(E), D + 2)]
        import sys; sys.path.insert(0, "src")
        import sens_year as sens
        e0 = sens.run(sens.BASE)[0]
        out["pct05"] = [float(x) for x in np.percentile(E[idx] / e0 - 1, [5, 50, 95]) * 100]
out["rank_stable_from"] = max(out["rank_stable_from05"], out["rank_stable_from10"])

# ---- structure vs efficiency
A = pd.read_csv("outputs/rev/A_structure_vs_eta_annual.csv")
out["structure"] = {r.case: float(r.d_pct) for r in A.itertuples()}

# ---- stack
B = pd.read_csv("outputs/rev/B_lower_bound_stack.csv")
out["stack"] = {r.step: dict(pct=float(r.model_pct_oct), r17=float(r.ratio_17), r18=float(r.ratio_18), rfeb=float(r.ratio_feb10))
                for r in B.itertuples()}
summ = json.load(open("outputs/rev/summary.json"))
out["annual_all_lowest"] = summ["annual_all_lowest_pct"]
out["annual_all_lowest_ghi10"] = summ["annual_all_lowest_pct_ghi10"]
out["display_over_hioki"] = summ["display_over_hioki"]
# Boland alone, 17-18 Oct (from rev_analysis.log)
log = open("outputs/rev/rev_analysis.log").read()
line = [l for l in log.splitlines() if l.startswith("boland alone")][0]
vals = [float(x) for x in line.split("float64(")[1:] for x in [x.split(")")[0]]]
out["boland_alone"] = float(np.mean(vals))
base_ratio = np.mean([out["stack"]["baseline"]["r17"], out["stack"]["baseline"]["r18"]])
out["boland_ratio"] = float(base_ratio / (1 + out["boland_alone"] / 100))

# ---- metrics and leave-one-out
Cm = pd.read_csv("outputs/rev/C_metrics.csv")
out["metrics"] = {r["date"]: {k: (None if pd.isna(v) else (float(v) if k != "date" else v)) for k, v in r.items()}
                  for r in Cm.to_dict("records")}
for d in out["metrics"].values():
    d["hours"] = int(d["hours"])
L = pd.read_csv("outputs/rev/C_leave_one_out.csv")
l17 = L[L.cal == "2026-10-17"]
out["loo"] = {r.test: float(r.nMBE_pct) for r in l17.itertuples()}
out["loo"]["k"] = float(l17.k.iloc[0])

# ---- counters
Dc = pd.read_csv("outputs/rev/D_counters.csv").set_index("inverter")
out["counters"] = {k: dict(kwh=int(Dc.loc[k, "counter_kWh"]), y_cnt=float(Dc.loc[k, "counter_kWh_kWp_yr"]),
                           model=float(Dc.loc[k, "model_same_period_kWh"]), ratio=float(Dc.loc[k, "counter_over_model_same_period"]))
                   for k in ["left", "middle"]}

# ---- aliasing
S = pd.read_csv("outputs/rev/aliasing_summary.csv", index_col=[0, 1])
fr, lk = "f 59.95-60.05 Hz", "f = 60.000 Hz (locked)"
g = lambda st, n: float(S.loc[(st, n), "max_abs_pct"])
n10, n20, n200 = "10 ms (thin-out 5, Oct 2026)", "20 ms (2025-26 records)", "200 ms (thin-out 100, avoided)"
out["aliasing"] = dict(ncases=int(len(pd.read_csv("outputs/rev/aliasing_mc.csv"))),
                       max10_free=g(fr, n10), max20_free=g(fr, n20), max200_free=g(fr, n200),
                       max10_locked=g(lk, n10), max20_locked=g(lk, n20), max200_locked=g(lk, n200))

json.dump(out, open("paper_rev/numbers.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("sobol05", "sobol10", "metrics", "structure", "stack")}, indent=1))
for k in ("sobol05", "sobol10"):
    print(k, {f: (round(v["ST"], 3), round(v["ST_conf"], 3)) for f, v in out[k].items()})
