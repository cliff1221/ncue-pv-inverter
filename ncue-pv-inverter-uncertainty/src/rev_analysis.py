"""Reviewer points 1, 5, 6, 7: extra analyses for the revised paper.

  A. Inverter: model structure vs assumed efficiency (annual 2023 and 17-18 Oct 2026)
  B. Lower-bound stack with EVERY factor at its lowest setting (incl. isotropic, Boland)
  C. Error metrics (MBE, nMBE, RMSE, nRMSE, r) for all clear-sky records
     and a leave-one-day-out test of a single empirical loss factor
  D. Long-term check: inverter lifetime energy counters vs as-built annual model
Run from repo root:  PYTHONPATH=src python src/rev_analysis.py
Output: outputs/rev/*.csv and printed summary.
"""
import os, json
import numpy as np, pandas as pd, pvlib
import config as cfg
import inverter_model as im
import sens_year as sens
from weather import cwa_day_file, make_location

os.makedirs("outputs/rev", exist_ok=True)
TZ = cfg.SITE["tz"]
R = {}

# ------------------------------------------------------------------ helpers
def inv_ac(pdc, pac0, structure, eta):
    """structure: 'constant' (eta = constant efficiency) or 'pvwatts' (eta = nominal efficiency)."""
    if structure == "constant":
        raw = pdc * eta
    else:
        pdc0 = pac0 / eta
        raw = pd.Series(im._pvwatts_unclipped(pdc.values, pdc0, eta), index=pdc.index)
    return raw.clip(upper=pac0)


def pvwatts_peak(eta_nom):
    z = np.linspace(0.01, 1.0, 100000)
    return float((eta_nom / im.ETA_REF * (-0.0162 * z - 0.0059 / z + 0.9858)).max())


ETA_NOM_EQ_PEAK = {k: v["eta_peak"] / (pvwatts_peak(1.0)) for k, v in cfg.INVERTERS.items()}

ASB = {"INV50_A": 145, "INV50_B": 140, "INV30": 87}          # as-built: left, middle, right
PAC = {k: v["pac_w"] for k, v in cfg.INVERTERS.items()}
ETAP = {k: v["eta_peak"] for k, v in cfg.INVERTERS.items()}


def annual_dc_per_module(p=None):
    """DC power per module (W), hourly 2023, baseline chain of sens_year.run."""
    p = dict(sens.BASE, **(p or {}))
    ghi = sens.GHI0 * (1.0 + p["galat_GHI"])
    sp, am, ex = sens.SP[p["geser_waktu"]]
    dni, dhi = sens.decompose(p["dekomposisi_GHI"], ghi, sp)
    poa = pvlib.irradiance.get_total_irradiance(
        23.0, 180.0, sp["apparent_zenith"], sp["azimuth"], dni, ghi, dhi, dni_extra=ex, airmass=am,
        albedo=p["albedo"], model=p["transposisi"])["poa_global"].fillna(0.0).clip(lower=0.0)
    tc = pvlib.temperature.ross(poa, sens.TAIR, p["NOCT"])
    pm = pvlib.pvsystem.pvwatts_dc(poa, tc, cfg.MODULE["pmax_stc_w"], cfg.MODULE["gamma_pdc"], 25.0)
    return (pm * (1 - p["rugi_DC"])).clip(lower=0.0)


def annual_ac(structure, eta_of, pm=None):
    pm = annual_dc_per_module() if pm is None else pm
    per = {k: float(inv_ac(pm * n, PAC[k], structure, eta_of(k)).sum()) / 1e3 for k, n in ASB.items()}
    return sum(per.values()), per


# ------------------------------------------------------------------ A. structure vs efficiency
pm0 = annual_dc_per_module()
e_ref, per_ref = annual_ac("pvwatts", lambda k: ETAP[k], pm0)          # = PVWatts-DS, as-built
rows = []
def addA(label, structure, eta_of, group):
    e, _ = annual_ac(structure, eta_of, pm0)
    rows.append(dict(group=group, case=label, E_MWh=e / 1e3, d_pct=(e / e_ref - 1) * 100))

addA("PVWatts, eta_nom = datasheet peak (PVWatts-DS, ref.)", "pvwatts", lambda k: ETAP[k], "ref")
for eta in [0.96, 0.98, 0.985]:
    addA(f"constant eta = {eta}", "constant", lambda k, e=eta: e, f"same eta {eta}")
    addA(f"PVWatts eta_nom = {eta}", "pvwatts", lambda k, e=eta: e, f"same eta {eta}")
addA("constant eta = datasheet peak", "constant", lambda k: ETAP[k], "same peak")
addA("PVWatts, peak of curve = datasheet peak", "pvwatts", lambda k: ETA_NOM_EQ_PEAK[k], "same peak")
for eta in [0.96, 0.97, 0.98, 0.985]:
    addA(f"PVWatts eta_nom = {eta}", "pvwatts", lambda k, e=eta: e, "efficiency sweep")
A = pd.DataFrame(rows).drop_duplicates("case", keep="first")
A.to_csv("outputs/rev/A_structure_vs_eta_annual.csv", index=False)
print("== A. annual (as-built, 2023): structure vs efficiency\n", A.round(3).to_string(index=False))
print("pvwatts peak efficiency for eta_nom=1:", round(pvwatts_peak(1.0), 5),
      "-> eta_nom giving datasheet peak:", {k: round(v, 4) for k, v in ETA_NOM_EQ_PEAK.items()})
R["annual_asbuilt_MWh"] = e_ref / 1e3

# ------------------------------------------------------------------ validation chain
SUB = {"L145": ("INV50_A", 145), "M140": ("INV50_B", 140), "R87": ("INV30", 87)}

def val_dc_per_module(w, loss=0.087, noct=46.0, transp="perez", iam_ar=None, gscale=1.0, decomp="erbs"):
    site = make_location(); t = w.index
    sp = site.get_solarposition(t); ex = pvlib.irradiance.get_extra_radiation(t)
    am = site.get_airmass(t, solar_position=sp)["airmass_relative"]
    ghi = w.ghi.fillna(0) * gscale
    if decomp == "erbs":
        dni, dhi = w.dni * gscale, w.dhi * gscale
    else:
        doy = pd.Series(t.dayofyear, index=t)
        r = pvlib.irradiance.boland(ghi, sp["zenith"], doy)
        dni = pd.Series(np.asarray(r["dni"], float), index=t).fillna(0).where(sp["zenith"] < 87, 0).clip(lower=0)
        dhi = pd.Series(np.asarray(r["dhi"], float), index=t).fillna(0).clip(lower=0)
    tot = pvlib.irradiance.get_total_irradiance(23.0, 180.0, sp["apparent_zenith"], sp["azimuth"], dni, ghi, dhi,
                                                dni_extra=ex, airmass=am, albedo=cfg.ALBEDO, model=transp)
    poa = tot["poa_global"].fillna(0).clip(lower=0)
    if iam_ar is not None:
        aoi = pvlib.irradiance.aoi(23.0, 180.0, sp["apparent_zenith"], sp["azimuth"])
        ib = pvlib.iam.martin_ruiz(aoi, a_r=iam_ar).fillna(0)
        idf = pvlib.iam.marion_diffuse("martin_ruiz", 23.0, a_r=iam_ar)
        poa = (tot["poa_direct"].fillna(0) * ib + tot["poa_sky_diffuse"].fillna(0) * idf["sky"] +
               tot["poa_ground_diffuse"].fillna(0) * idf["ground"]).clip(lower=0)
    tc = pvlib.temperature.ross(poa_global=poa, temp_air=w.temp_air, noct=noct)
    return (pvlib.pvsystem.pvwatts_dc(poa, tc, 375.0, cfg.MODULE["gamma_pdc"], 25.0) * (1 - loss)).clip(lower=0)


def val_model(w, structure="pvwatts", eta_of=lambda k: ETAP[k], **kw):
    pm = val_dc_per_module(w, **kw)
    return sum(inv_ac(pm * n, PAC[inv], structure, eta_of(inv)) for inv, n in SUB.values()) / 1e3  # kW


H = pd.read_csv("outputs/validation/hourly_variants.csv")
meas = H[H.variant == "base"][["date", "hour", "minutes", "P_meas"]]
WX = {}

def wx(date):
    if date not in WX:
        WX[date] = cwa_day_file(f"data/validation/codis_days/467270-{date}.csv")
    return WX[date]


def ratio(date, **kw):
    w = wx(date); day0 = pd.Timestamp(date, tz=TZ)
    pmod = val_model(w, **kw)
    m = pd.DataFrame(dict(hour=[int(round((t - day0).total_seconds() / 3600 + 0.5)) for t in pmod.index], P_model=pmod.values))
    g = m.merge(meas[meas.date == date], on="hour")
    g = g[g.P_model > 1]
    return float((g.P_meas.clip(lower=0) * g.minutes).sum() / (g.P_model * g.minutes).sum()), g


OCT = ["2026-10-17", "2026-10-18"]
rowsA2 = []
for lbl, kw in [("PVWatts-DS (ref.)", {}),
                ("constant eta=0.96", dict(structure="constant", eta_of=lambda k: 0.96)),
                ("PVWatts eta_nom=0.96", dict(eta_of=lambda k: 0.96)),
                ("constant eta=datasheet peak", dict(structure="constant")),
                ("PVWatts peak=datasheet peak", dict(eta_of=lambda k: ETA_NOM_EQ_PEAK[k]))]:
    rs = [ratio(d, **kw)[0] for d in OCT]
    rowsA2.append(dict(case=lbl, ratio_17=rs[0], ratio_18=rs[1]))
A2 = pd.DataFrame(rowsA2); A2.to_csv("outputs/rev/A_structure_vs_eta_oct.csv", index=False)
print("\n== A2. 17-18 Oct measured/model\n", A2.round(4).to_string(index=False))

# ------------------------------------------------------------------ B. lower-bound stacks
gen = dict(eta_of=lambda k: 0.96)
STACKS = [
    ("baseline", {}),
    ("+ PVWatts-G", dict(**gen)),
    ("+ DC loss 11.4 %", dict(**gen, loss=0.114)),
    ("+ NOCT 48", dict(**gen, loss=0.114, noct=48.0)),
    ("+ IAM (Martin-Ruiz)", dict(**gen, loss=0.114, noct=48.0, iam_ar=0.16)),
    ("+ isotropic transposition", dict(**gen, loss=0.114, noct=48.0, iam_ar=0.16, transp="isotropic")),
    ("+ Boland decomposition", dict(**gen, loss=0.114, noct=48.0, iam_ar=0.16, transp="isotropic", decomp="boland")),
    ("+ GHI -5 %", dict(**gen, loss=0.114, noct=48.0, iam_ar=0.16, transp="isotropic", decomp="boland", gscale=0.95)),
    ("+ GHI -10 % (instead of -5 %)", dict(**gen, loss=0.114, noct=48.0, iam_ar=0.16, transp="isotropic", decomp="boland", gscale=0.90)),
]
base_E = {d: ratio(d)[1].P_model.sum() for d in OCT + ["2026-02-10"]}
rowsB = []
for lbl, kw in STACKS:
    r = {}
    for d in OCT + ["2026-02-10"]:
        rr, g = ratio(d, **kw); r[d] = (rr, g.P_model.sum() / base_E[d] * 100)
    rowsB.append(dict(step=lbl, model_pct_oct=np.mean([r[d][1] for d in OCT]),
                      ratio_17=r[OCT[0]][0], ratio_18=r[OCT[1]][0], ratio_feb10=r["2026-02-10"][0]))
Bt = pd.DataFrame(rowsB); Bt.to_csv("outputs/rev/B_lower_bound_stack.csv", index=False)
print("\n== B. stacked lower bounds\n", Bt.round(3).to_string(index=False))
# single changes (same days) for the two new factors
for lbl, kw in [("isotropic alone", dict(transp="isotropic")), ("boland alone", dict(decomp="boland")),
                ("haydavies alone", dict(transp="haydavies"))]:
    print(lbl, [round(ratio(d, **kw)[1].P_model.sum() / base_E[d] * 100 - 100, 2) for d in OCT])

# annual: all nine factors at their lowest setting jointly
low = dict(dekomposisi_GHI="boland", transposisi="isotropic", model_suhu_sel="ross", geser_waktu="awal",
           pemetaan="b", model_inverter="pvwatts_gen", NOCT=48.0, rugi_DC=0.114, galat_GHI=-0.05)
e_low = sens.run(dict(sens.BASE, **low))[0]; e_b = sens.run(sens.BASE)[0]
R["annual_all_lowest_pct"] = (e_low / e_b - 1) * 100
low10 = dict(low, galat_GHI=-0.10)
R["annual_all_lowest_pct_ghi10"] = (sens.run(dict(sens.BASE, **low10))[0] / e_b - 1) * 100
print("annual, all nine at lowest (GHI -5 / -10):", round(R["annual_all_lowest_pct"], 2), round(R["annual_all_lowest_pct_ghi10"], 2))

# ------------------------------------------------------------------ C. metrics, all clear-sky records
CLEAR = ["2026-10-17", "2026-10-18", "2026-02-10", "2025-12-21", "2025-08-07"]
rowsC = []; Gs = {}
for d in CLEAR:
    _, g = ratio(d); g = g[g.minutes >= 20]          # same hour selection as Fig. 8 of the paper
    w_ = g.minutes / g.minutes.sum()                   # weight each hour by its recorded minutes
    e = g.P_model - g.P_meas.clip(lower=0); pm_ = (g.P_meas.clip(lower=0) * w_).sum()
    mbe = (e * w_).sum(); rmse = np.sqrt((e ** 2 * w_).sum())
    Gs[d] = g
    rowsC.append(dict(date=d, hours=len(g), minutes=int(g.minutes.sum()), P_mean_meas=pm_, MBE_kW=mbe,
                      nMBE_pct=mbe / pm_ * 100, RMSE_kW=rmse, nRMSE_pct=rmse / pm_ * 100,
                      r=np.corrcoef(g.P_meas, g.P_model)[0, 1] if len(g) > 2 else np.nan,
                      ratio=(g.P_meas.clip(lower=0) * g.minutes).sum() / (g.P_model * g.minutes).sum()))
C = pd.DataFrame(rowsC); C.to_csv("outputs/rev/C_metrics.csv", index=False)
print("\n== C. metrics (full hours, P_model>1 kW)\n", C.round(3).to_string(index=False))
# leave-one-day-out: calibrate k = E_meas/E_model on one day, apply to the others
rowsL = []
for dcal in CLEAR:
    gc = Gs[dcal]; k = (gc.P_meas.clip(lower=0) * gc.minutes).sum() / (gc.P_model * gc.minutes).sum()
    for d in CLEAR:
        if d == dcal: continue
        g = Gs[d]; w_ = g.minutes
        e = k * g.P_model - g.P_meas.clip(lower=0)
        rowsL.append(dict(cal=dcal, k=k, test=d,
                          nMBE_pct=(e * w_).sum() / (g.P_meas.clip(lower=0) * w_).sum() * 100))
L = pd.DataFrame(rowsL); L.to_csv("outputs/rev/C_leave_one_out.csv", index=False)
print("\n== C2. calibrated on 17 Oct (k=%.3f), nMBE on other days:" % L[L.cal == '2026-10-17'].k.iloc[0])
print(L[L.cal == "2026-10-17"][["test", "nMBE_pct"]].round(1).to_string(index=False))
print("range of k over clear days:", round(L.k.min(), 3), round(L.k.max(), 3))

# ------------------------------------------------------------------ D. long-term counters
# readings 18 Oct 2026 16:57-16:58, commissioning 17 Apr 2023 (installation date in device info)
days = (pd.Timestamp("2026-10-18 16:57") - pd.Timestamp("2023-04-17 12:00")).total_seconds() / 86400
CNT = {"INV50_A": (269093, 145, "left"), "INV50_B": (264693, 140, "middle")}
_, per = annual_ac("pvwatts", lambda k: ETAP[k], pm0)
# Same calendar period: 2023 weather used as a typical year, repeated for each calendar day
# from 17 Apr 2023 to 18 Oct 2026 (the period contains four summers but only three winters).
cal = pd.date_range("2023-04-17", "2026-10-17", freq="D")
rowsD = []
for k, (kwh, n, pos) in CNT.items():
    kwp = n * 0.375
    ac_h = inv_ac(pm0 * n, PAC[k], "pvwatts", ETAP[k]) / 1e3            # kW, hourly 2023
    daily = ac_h.groupby(ac_h.index.strftime("%m-%d")).sum()           # kWh per calendar day
    daily["02-29"] = daily["02-28"]                                     # 2024 leap day
    e_period = float(daily.reindex(cal.strftime("%m-%d")).sum()) + 0.95 * daily["10-18"]   # to 16:57 on 18 Oct
    y_cnt = kwh / kwp / days * 365.0
    y_mod = per[k] / kwp
    rowsD.append(dict(inverter=pos, modules=n, kWp=kwp, counter_kWh=kwh, days=days, counter_kWh_kWp_yr=y_cnt,
                      model2023_kWh_kWp_yr=y_mod, model_same_period_kWh=e_period,
                      counter_over_model_same_period=kwh / e_period))
Dt = pd.DataFrame(rowsD); Dt.to_csv("outputs/rev/D_counters.csv", index=False)
print("\n== D. lifetime counters vs annual model (2023 weather, as-built, PVWatts-DS)\n", Dt.round(3).to_string(index=False))

# display vs Hioki on 18 Oct: sum of the three 'Today' readings (16:57-16:59) vs Hioki energy to 16:58
M = pd.read_csv("outputs/validation/minute_all.csv", parse_dates=["t"])
M["t"] = pd.to_datetime(M.t, utc=True).dt.tz_convert(TZ)
s = M[(M.t >= pd.Timestamp("2026-10-18", tz=TZ)) & (M.t <= pd.Timestamp("2026-10-18 16:58", tz=TZ))]
e_h = s.P_kW.clip(lower=0).sum() / 60
e_day = M[(M.t >= pd.Timestamp("2026-10-18", tz=TZ)) & (M.t < pd.Timestamp("2026-10-19", tz=TZ))].P_kW.clip(lower=0).sum() / 60
R.update(hioki_18oct_to_1658=e_h, hioki_18oct_day=e_day, displays_sum=219 + 219 + 134,
         display_over_hioki=(219 + 219 + 134) / e_h, counter_days=days)
print("\nHioki 18 Oct to 16:58: %.1f kWh (whole day %.1f); displays 572 kWh -> ratio %.3f" % (e_h, e_day, 572 / e_h))
json.dump(R, open("outputs/rev/summary.json", "w"), indent=1)

# ------------------------------------------------------------------ hourly series for the revised Fig. 6
full = dict(eta_of=lambda k: 0.96, loss=0.114, noct=48.0, iam_ar=0.16, transp="isotropic", decomp="boland", gscale=0.95)
hr = []
for d in OCT:
    _, gb = ratio(d); _, gs = ratio(d, **full)
    m = gb[["hour", "P_model", "P_meas", "minutes"]].rename(columns={"P_model": "P_base"})
    m = m.merge(gs[["hour", "P_model"]].rename(columns={"P_model": "P_stack"}), on="hour"); m["date"] = d
    hr.append(m)
pd.concat(hr).to_csv("outputs/rev/hourly_base_stack_oct.csv", index=False)
