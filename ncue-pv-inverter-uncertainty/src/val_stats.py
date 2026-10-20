import numpy as np, pandas as pd, json
H = pd.read_csv('outputs/validation/hourly_variants.csv'); M = pd.read_csv('outputs/validation/minute_all.csv', parse_dates=['t'])
res = {}
oc = H[H.date.isin(['2026-10-17', '2026-10-18'])].copy(); oc['Pm'] = oc.P_meas.clip(lower=0)
# --- energi dan rasio per hari & varian
print("== Okt 17-18: E_meas/E_model per varian")
tab = {}
for (d, v), g in oc.groupby(['date', 'variant']):
    tab[(d, v)] = (g.Pm.sum(), g.P_model.sum())
for v in oc.variant.unique():
    r = [tab[(d, v)][0]/tab[(d, v)][1] for d in ['2026-10-17', '2026-10-18']]
    chg = [(tab[(d, v)][1]/tab[(d, 'base')][1]-1)*100 for d in ['2026-10-17', '2026-10-18']]
    print(f"{v:13s} meas/model {r[0]:.3f} {r[1]:.3f} | model change vs base {chg[0]:+.1f}% {chg[1]:+.1f}%")
for d in ['2026-10-17', '2026-10-18']:
    em, ep = tab[(d, 'base')]; print(d, 'E_meas', round(em, 1), 'E_model', round(ep, 1))
# --- metrik per jam (siang) base
b = oc[(oc.variant == 'base') & (oc.ghi > 20)]
for d, g in b.groupby('date'):
    mbe = (g.P_model-g.Pm).mean(); rmse = np.sqrt(((g.P_model-g.Pm)**2).mean()); r = np.corrcoef(g.Pm, g.P_model)[0, 1]
    sl = (g.Pm*g.P_model).sum()/(g.P_model**2).sum()
    print(d, f"MBE {mbe:.1f} kW ({mbe/g.Pm.mean()*100:.0f}%), RMSE {rmse:.1f} kW ({rmse/g.Pm.mean()*100:.0f}%), r {r:.3f}, slope_meas_on_model {sl:.3f}, n {len(g)}")
# --- rasio per jam rata-rata 2 hari
rh = b.assign(ratio=b.Pm/b.P_model).groupby('hour').ratio.agg(['mean', 'min', 'max']).round(3); print(rh.to_string())
# --- sentroid
for d, g in b.groupby('date'):
    cm = (g.hour*g.Pm).sum()/g.Pm.sum(); cp = (g.hour*g.P_model).sum()/g.P_model.sum()
    am = g[g.hour <= 12].Pm.sum()/g[g.hour <= 12].P_model.sum(); pm = g[g.hour > 12].Pm.sum()/g[g.hour > 12].P_model.sum()
    print(d, f"centroid meas {cm-0.5:.2f} h model {cp-0.5:.2f} h; ratio AM {am:.3f} PM {pm:.3f}")
# --- PR
for d, g in b.groupby('date'):
    H_poa = g.poa.sum()/1000; PR = g.Pm.sum()/(139.5*H_poa); PRm = g.P_model.sum()/(139.5*H_poa)
    print(d, f"H_poa {H_poa:.2f} kWh/m2  PR_meas {PR:.3f}  PR_model {PRm:.3f}  Y_f {g.Pm.sum()/139.5:.2f} kWh/kWp")
# --- statistik per-menit 3 hari
Mx = M[(M.t >= '2026-10-17') & (M.t < '2026-10-19')].set_index('t').P_kW
for d in ['2026-10-17', '2026-10-18']:
    s = Mx[d]; day = s[s > 1]
    print(d, 'peak', round(s.max(), 1), 'p99', round(s.quantile(.99), 1), 'frac>65kW(50%)', round((s > 65).mean(), 4), 'max |dP/min|', round(s.diff().abs().max(), 1), 'minutes>1kW', len(day))
# --- jam stabil, semua kampanye
A = H[(H.variant == 'base')].copy()
A['ratio'] = A.P_meas/A.P_model
st = A[(A.minutes >= 45) & (A.P_meas > 5) & (A.cv < 0.08)]
print("== jam stabil (>=45 menit, P>5kW, CV<0.08):"); print(st.groupby('date').ratio.agg(['size', 'median', 'min', 'max']).round(3))
print("pooled slope", round((st.P_meas*st.P_model).sum()/(st.P_model**2).sum(), 3), 'n', len(st))
print("== semua kampanye, rasio dibobot menit untuk jam P_model>1:")
for d, g in A.groupby('date'):
    g = g[g.P_model > 1]; print(d, round((g.P_meas*g.minutes).sum()/(g.P_model*g.minutes).sum(), 3), 'cv median', round(g.cv.median(), 3), 'hours', len(g))
