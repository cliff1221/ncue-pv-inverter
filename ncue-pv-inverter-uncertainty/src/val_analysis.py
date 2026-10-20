"""Validasi lapangan: model as-built vs Hioki; varian model untuk 'budget closure'. Keluaran: outputs/validation/*.csv"""
import numpy as np, pandas as pd, pvlib
import config as cfg
from weather import cwa_day_file, make_location
import inverter_model as im
TZ = cfg.SITE['tz']
SUB = {"L145": 145, "M140": 140, "R87": 87}
MAP = {"INV50_A": ["L145"], "INV50_B": ["M140"], "INV30": ["R87"]}
cfg.SUBARRAYS = {k: dict(n_modules=n, tilt=23.0, azimuth=180.0) for k, n in SUB.items()}
FILES = {
 "2026-10-17": "data/validation/codis_days", "2026-10-18": "data/validation/codis_days",
 "2025-06-17": "data/validation/codis_days", "2025-08-07": "data/validation/codis_days", "2025-12-21": "data/validation/codis_days",
 "2025-10-23": "data/validation/codis_days", "2025-10-27": "data/validation/codis_days", "2026-02-10": "data/validation/codis_days", "2026-04-24": "data/validation/codis_days"}
# ---------------- ukuran: per-menit gabungan
a = pd.read_csv('data/validation/hioki_minute_oct2026.csv', parse_dates=['waktu_mulai'])[['waktu_mulai', 'P_kW']]
b = pd.read_csv('data/validation/hioki_minute_2025_records.csv', parse_dates=['waktu_mulai'])[['waktu_mulai', 'P_kW']]
c = pd.read_csv('data/validation/hioki_minute_2025_2026_records.csv', parse_dates=['waktu_mulai'])[['waktu_mulai', 'P_kW']]
M = pd.concat([a, b, c]).drop_duplicates('waktu_mulai').sort_values('waktu_mulai')
M['t'] = M.waktu_mulai.dt.tz_localize(TZ) + pd.Timedelta(seconds=30)   # tengah menit
M = M.set_index('t'); M.to_csv('outputs/validation/minute_all.csv')
# ---------------- model
def dc_table(w, loss=0.087, noct=46.0, transp="perez", iam_ar=None, gscale=1.0):
    site = make_location(); t = w.index
    sp = site.get_solarposition(t); ex = pvlib.irradiance.get_extra_radiation(t)
    am = site.get_airmass(t, solar_position=sp)["airmass_relative"]
    ghi, dni, dhi = w.ghi*gscale, w.dni*gscale, w.dhi*gscale
    out = pd.DataFrame(index=t)
    for name, n in SUB.items():
        tot = pvlib.irradiance.get_total_irradiance(23.0, 180.0, sp["apparent_zenith"], sp["azimuth"], dni, ghi, dhi,
                dni_extra=ex, airmass=am, albedo=cfg.ALBEDO, model=transp)
        poa = tot["poa_global"].fillna(0).clip(lower=0)
        if iam_ar is not None:
            aoi = pvlib.irradiance.aoi(23.0, 180.0, sp["apparent_zenith"], sp["azimuth"])
            ib = pvlib.iam.martin_ruiz(aoi, a_r=iam_ar).fillna(0)
            idf = pvlib.iam.marion_diffuse("martin_ruiz", 23.0, a_r=iam_ar)
            poa = (tot["poa_direct"].fillna(0)*ib + tot["poa_sky_diffuse"].fillna(0)*idf["sky"] +
                   tot["poa_ground_diffuse"].fillna(0)*idf["ground"]).clip(lower=0)
        tc = pvlib.temperature.ross(poa_global=poa, temp_air=w.temp_air, noct=noct)
        pdc = pvlib.pvsystem.pvwatts_dc(poa, tc, 375.0*n, cfg.MODULE["gamma_pdc"], 25.0)
        out[f"DC_{name}"] = (pdc*(1-loss)).clip(lower=0); out[f"poa_{name}"] = poa; out[f"tcell_{name}"] = tc
    return out
VAR = {  # nama: (kwargs untuk dc_table, model inverter)
 "base": ({}, "pvwatts_ds"), "inv_constant": ({}, "constant"), "inv_gen": ({}, "pvwatts_gen"),
 "loss0": (dict(loss=0.0), "pvwatts_ds"), "loss11.4": (dict(loss=0.114), "pvwatts_ds"),
 "ghi-5": (dict(gscale=0.95), "pvwatts_ds"), "ghi+5": (dict(gscale=1.05), "pvwatts_ds"),
 "ghi-10": (dict(gscale=0.90), "pvwatts_ds"), "ghi+10": (dict(gscale=1.10), "pvwatts_ds"),
 "noct44": (dict(noct=44.0), "pvwatts_ds"), "noct48": (dict(noct=48.0), "pvwatts_ds"),
 "isotropic": (dict(transp="isotropic"), "pvwatts_ds"), "iam": (dict(iam_ar=0.16), "pvwatts_ds"),
 "c1": ({}, "pvwatts_gen"), "c2": (dict(loss=0.114), "pvwatts_gen"), "c3": (dict(loss=0.114, noct=48.0), "pvwatts_gen"),
 "c4": (dict(loss=0.114, noct=48.0, iam_ar=0.16), "pvwatts_gen"),
 "stack5": (dict(gscale=0.95, loss=0.114, noct=48.0, iam_ar=0.16), "pvwatts_gen"),
 "stack10": (dict(gscale=0.90, loss=0.114, noct=48.0, iam_ar=0.16), "pvwatts_gen")}
rows = []; krows = []
for date, d in FILES.items():
    w = cwa_day_file(f"{d}/467270-{date}.csv"); day0 = pd.Timestamp(date, tz=TZ)
    cs = make_location().get_clearsky(w.index)
    krows.append(dict(date=date, ghi_MJ=w.ghi.sum()*3.6/1000, cs_MJ=cs.ghi.sum()*3.6/1000, kt=w.ghi.sum()/cs.ghi.sum(), sunshine_h=w.sunshine_h.sum(), rain_mm=w.precip_mm.sum()))
    for v, (kw, invm) in VAR.items():
        dc = dc_table(w, **kw); ac, _, _ = im.simulate_ac(dc, MAP, invm)
        tot = ac.sum(axis=1)/1e3
        poa = dc[[f"poa_{k}" for k in SUB]].mul(list(SUB.values()), axis=1).sum(axis=1)/sum(SUB.values())
        for t, p in tot.items():
            rows.append(dict(date=date, hour=int(round((t-day0).total_seconds()/3600+0.5)), variant=v, P_model=p,
                             poa=poa[t], ghi=w.loc[t, 'ghi'], ta=w.loc[t, 'temp_air'], sunshine=w.loc[t, 'sunshine_h']))
V = pd.DataFrame(rows)
# ---------------- ukuran per jam (label = akhir jam)
mrows = []
for date in FILES:
    day0 = pd.Timestamp(date, tz=TZ)
    for h in range(1, 25):
        s = M.loc[(M.index > day0+pd.Timedelta(hours=h-1)) & (M.index <= day0+pd.Timedelta(hours=h)), 'P_kW']
        if len(s) >= 20:
            mrows.append(dict(date=date, hour=h, minutes=len(s), P_meas=s.mean(), cv=s.std()/s.mean() if s.mean() > 1 else np.nan,
                              P_min=s.min(), P_max=s.max()))
Mh = pd.DataFrame(mrows)
H = V.merge(Mh, on=['date', 'hour'], how='inner')
H.to_csv('outputs/validation/hourly_variants.csv', index=False)
V.to_csv('outputs/validation/model_variants_all.csv', index=False)
# cek terhadap hasil sebelumnya
old = pd.read_csv('outputs/validation/compare_hourly_oct2026.csv'); o = old[old.model == 'pvwatts_ds'][['date', 'hour', 'P_model']]
chk = V[V.variant == 'base'].merge(o, on=['date', 'hour'], suffixes=('', '_old'))
print("maks selisih base vs hitungan lama (kW):", (chk.P_model-chk.P_model_old).abs().max())
print(H[H.variant == 'base'].groupby('date').size())

pd.DataFrame(krows).to_csv('outputs/validation/campaign_sky.csv', index=False)
