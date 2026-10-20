import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
plt.rcParams.update({"font.family": "serif", "font.serif": ["Liberation Serif", "Times New Roman"], "font.size": 7.5,
                     "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6, "axes.spines.top": False, "axes.spines.right": False})
OUT = "paper_figs/"; BL, OR, GR, RD = "#2a7ab0", "#d9822b", "#7a7a7a", "#b23a3a"
H = pd.read_csv('outputs/validation/hourly_variants.csv'); M = pd.read_csv('outputs/validation/minute_all.csv', parse_dates=['t']); M['t'] = pd.to_datetime(M.t, utc=True).dt.tz_convert('Asia/Taipei')
K = pd.read_csv('outputs/validation/campaign_sky.csv')
def box(ax, x, y, w, h, txt, fc="#eef3f8", ec="#2a7ab0", fs=6.6, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015", fc=fc, ec=ec, lw=0.7))
    ax.text(x+w/2, y+h/2, txt, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", linespacing=1.15)
def arrow(ax, p, q, color="#444"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=7, lw=0.8, color=color, shrinkA=0, shrinkB=0))
# ---------- Fig: lokasi/sistem + titik ukur
fig, ax = plt.subplots(figsize=(3.3, 2.5)); ax.set_xlim(0, 1.04); ax.set_ylim(0, 1.13); ax.axis("off")
data = [("145 modules\n54.4 kWp", "Inverter A\n50 kW", 0.76), ("140 modules\n52.5 kWp", "Inverter B\n50 kW", 0.47), ("87 modules\n32.6 kWp", "Inverter C\n30 kW", 0.18)]
for pv, inv, y in data:
    box(ax, 0.02, y, 0.25, 0.17, pv, fc="#f4ecd8", ec=OR); box(ax, 0.38, y, 0.2, 0.17, inv, fc="#e3eef7", ec=BL)
    arrow(ax, (0.27, y+0.085), (0.38, y+0.085)); ax.plot([0.58, 0.66], [y+0.085, y+0.085], color="#444", lw=0.9)
ax.plot([0.66, 0.66], [0.265, 0.845], color="#444", lw=1.4); ax.text(0.7, 0.93, "AC bus\n(3-phase, 3-wire)", ha="center", fontsize=6.3)
ax.add_patch(Circle((0.78, 0.55), 0.045, fc="#fbe9e9", ec=RD, lw=0.9)); ax.plot([0.66, 0.735], [0.55, 0.55], color="#444", lw=0.9)
ax.text(0.69, 0.47, "Hioki MR8875:\n3 clamps +\n3 voltage leads", ha="left", va="top", fontsize=6.2, color=RD, linespacing=1.15)
arrow(ax, (0.825, 0.55), (0.9, 0.55)); box(ax, 0.9, 0.49, 0.095, 0.12, "Grid", fc="#eee", ec=GR, fs=6.3)
ax.text(0.0, 1.125, "Rooftop array\n372 modules, 23° tilt, south", ha="left", fontsize=6.2, va="top", linespacing=1.1)
ax.text(0.5, 0.02, "Measurement point downstream of all three inverters (sum of outputs)", ha="center", fontsize=6.3, style="italic")
plt.savefig(OUT+"fig_site.png", dpi=300, bbox_inches="tight", pad_inches=0.03); plt.close()
# ---------- Fig: alur studi
fig, ax = plt.subplots(figsize=(3.3, 3.1)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
box(ax, 0.02, 0.84, 0.46, 0.13, "Datasheets and\npublic data"); box(ax, 0.52, 0.84, 0.46, 0.13, "Hioki MR8875\n3 days + 7 records", fc="#f4ecd8", ec=OR)
box(ax, 0.02, 0.63, 0.46, 0.13, "pvlib model chain\n(as-built mapping)"); box(ax, 0.52, 0.63, 0.46, 0.13, "Two-wattmeter\npower, 3-phase", fc="#f4ecd8", ec=OR)
arrow(ax, (0.25, 0.84), (0.25, 0.76)); arrow(ax, (0.75, 0.84), (0.75, 0.76), OR)
box(ax, 0.02, 0.41, 0.22, 0.14, "Annual budget\nOAT + Sobol", fs=6.2); box(ax, 0.26, 0.41, 0.22, 0.14, "Hourly model,\nmeasured days", fs=6.2); box(ax, 0.52, 0.41, 0.46, 0.14, "1-min and hourly\nmean AC power", fc="#f4ecd8", ec=OR)
arrow(ax, (0.13, 0.63), (0.13, 0.55)); arrow(ax, (0.37, 0.63), (0.37, 0.55)); arrow(ax, (0.75, 0.63), (0.75, 0.55), OR)
box(ax, 0.12, 0.12, 0.76, 0.15, "Validation and budget closure\nmeasured vs modeled AC power", fc="#fbe9e9", ec=RD)
arrow(ax, (0.13, 0.41), (0.3, 0.27), BL); arrow(ax, (0.37, 0.41), (0.42, 0.27), BL); arrow(ax, (0.75, 0.41), (0.62, 0.27), OR)
plt.savefig(OUT+"fig_workflow.png", dpi=300, bbox_inches="tight", pad_inches=0.03); plt.close()
# ---------- Fig: 3 hari terukur
Mm = M[(M.t >= '2026-10-16 19:46') & (M.t <= '2026-10-19 18:05')].set_index('t').P_kW
fig, ax = plt.subplots(figsize=(3.3, 2.7))
ax.plot(Mm.index, Mm.clip(lower=0), color=BL, lw=0.6); ax.axhline(130, color=RD, lw=0.7, ls="--"); ax.text(Mm.index[40], 120, "inverter rating 130 kW", color=RD, fontsize=6.3)
for d, lab in [('2026-10-17', 'Sat 17'), ('2026-10-18', 'Sun 18'), ('2026-10-19', 'Mon 19')]:
    ax.text(pd.Timestamp(d+' 12:00', tz='Asia/Taipei'), 107, lab, ha="center", fontsize=6.5)
ax.set_ylim(0, 140); ax.set_ylabel("AC power, 1-min mean (kW)")
ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12], tz=Mm.index.tz)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M", tz=Mm.index.tz))
plt.tight_layout(); plt.savefig(OUT+"fig_meas3d.png", dpi=300); plt.close()
# ---------- Fig: model vs ukur 17-18 Okt
fig, axs = plt.subplots(2, 1, figsize=(3.3, 3.15), sharex=True)
for ax, d, lab in zip(axs, ['2026-10-17', '2026-10-18'], ['(a) 17 Oct 2026', '(b) 18 Oct 2026']):
    g = H[H.date == d]; b = g[g.variant == 'base'].set_index('hour'); s = g[g.variant == 'stack5'].set_index('hour'); h = np.arange(5, 20)
    ax.fill_between(h, s.P_model.reindex(h).fillna(0), b.P_model.reindex(h).fillna(0), color="#b7d3e8", lw=0, label="model, stacked lower bounds")
    ax.plot(h, b.P_model.reindex(h), color=BL, lw=1.0, label="model baseline")
    ax.plot(h, b.P_meas.clip(lower=0).reindex(h), color="k", lw=1.0, marker="o", ms=2.5, label="measured (Hioki)")
    ax.set_ylabel("AC power (kW)"); ax.text(0.02, 0.9, lab, transform=ax.transAxes, fontsize=7)
h_, l_ = axs[0].get_legend_handles_labels(); fig.legend([h_[2], h_[1], h_[0]], [l_[2], l_[1], l_[0]], loc="lower center", ncol=3, frameon=False, fontsize=6, handlelength=1.4, columnspacing=1.0); axs[1].set_xlabel("Hour label (end of hour, UTC+8)")
plt.tight_layout(rect=[0, 0.06, 1, 1]); plt.savefig(OUT+"fig_modelvs.png", dpi=300); plt.close()
# ---------- Fig: scatter jam
B = H[(H.variant == 'base') & (H.minutes >= 40) & (H.P_model > 5)].copy(); B['clear'] = B.sunshine >= 0.9
fig, ax = plt.subplots(figsize=(3.3, 3.0)); mx = 125
ax.plot([0, mx], [0, mx], color=GR, lw=0.7, ls=":"); ax.text(mx*0.93, mx*0.99, "1:1", color=GR, fontsize=6.5)
c = B[B.clear]; k = (c.P_meas*c.P_model).sum()/(c.P_model**2).sum(); ax.plot([0, mx], [0, k*mx], color=RD, lw=0.9)
ax.text(mx*0.98, 6, f"clear hours: slope {k:.2f}\n(n = {len(c)}, r = {np.corrcoef(c.P_meas, c.P_model)[0, 1]:.2f})", color=RD, fontsize=6.4, ha="right")
oc = c.date.isin(['2026-10-17', '2026-10-18']); ax.scatter(c[oc].P_model, c[oc].P_meas, s=11, color=BL, label="clear hours, 17-18 Oct 2026", zorder=3)
ax.scatter(c[~oc].P_model, c[~oc].P_meas, s=13, color=OR, marker="s", label="clear hours, other days", zorder=3)
n = B[~B.clear]; ax.scatter(n.P_model, n.P_meas, s=11, facecolors="none", edgecolors=GR, lw=0.7, label="other hours (cloud or edge of record)")
ax.set_xlim(0, mx); ax.set_ylim(0, mx); ax.set_xlabel("Modeled hourly AC power (kW)"); ax.set_ylabel("Measured hourly AC power (kW)"); ax.legend(frameon=False, fontsize=6.2, loc="upper left")
ax.set_aspect("equal"); plt.tight_layout(); plt.savefig(OUT+"fig_scatter.png", dpi=300); plt.close()
print("clear-hour slope", round(k, 3), "n clear", len(c), "n other", len(n), "r clear", round(np.corrcoef(c.P_meas, c.P_model)[0, 1], 3))
# ---------- Fig: rasio per jam
R = H[(H.variant == 'base') & (H.minutes >= 40) & (H.P_model > 10)].copy(); R['ratio'] = R.P_meas/R.P_model
fig, ax = plt.subplots(figsize=(3.3, 2.1))
for d, col, mk, lab in [('2026-10-17', BL, 'o', '17 Oct 2026'), ('2026-10-18', "#3d9970", 's', '18 Oct 2026'), ('2026-02-10', OR, '^', '10 Feb 2026'), ('2025-12-21', RD, 'D', '21 Dec 2025'), ('2025-08-07', GR, 'v', '7 Aug 2025')]:
    g = R[R.date == d]; ax.plot(g.hour, g.ratio, color=col, marker=mk, ms=3, lw=0.7 if len(g) > 3 else 0, label=lab)
ax.axhline(1, color="k", lw=0.6); ax.set_ylim(0.5, 1.3); ax.set_xlabel("Hour label (end of hour, UTC+8)"); ax.set_ylabel("Measured / modeled")
ax.legend(frameon=False, fontsize=6.2, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.24)); plt.tight_layout(); plt.savefig(OUT+"fig_ratio_hour.png", dpi=300); plt.close()
# ---------- Fig: budget closure
oc = H[H.date.isin(['2026-10-17', '2026-10-18'])]; E = {v: oc[oc.variant == v].P_model.sum() for v in oc.variant.unique()}; Em = oc[oc.variant == 'base'].P_meas.clip(lower=0).sum()
steps = [("Baseline model", 'base'), ("+ PVWatts-G inverter", 'c1'), ("+ DC loss 11.4 %", 'c2'), ("+ NOCT 48 °C", 'c3'), ("+ incidence-angle loss", 'c4'), ("+ GHI −5 %", 'stack5'), ("+ GHI −10 %", 'stack10')]
vals = [E[v]/E['base']*100 for _, v in steps]; meas = Em/E['base']*100
fig, ax = plt.subplots(figsize=(3.3, 2.25)); y = np.arange(len(steps))[::-1]
ax.barh(y, vals, color=[BL]+["#8fb8d6"]*5+["#c9d9e6"], height=0.62)
for yi, v in zip(y, vals): ax.text(v+0.6, yi, f"{v:.1f}", va="center", fontsize=6.5)
ax.axvline(meas, color=RD, lw=1.1); ax.text(meas-0.4, -0.95, f"measured {meas:.0f} %", color=RD, fontsize=6.6, ha="right", va="center")
ax.set_yticks(y); ax.set_yticklabels([s for s, _ in steps], fontsize=6.6); ax.set_xlim(70, 108); ax.set_ylim(-1.4, len(steps)-0.4)
ax.set_xlabel("Modeled energy, 17-18 Oct 2026 (% of baseline)"); plt.tight_layout(); plt.savefig(OUT+"fig_closure.png", dpi=300); plt.close()
print({k_: round(v, 1) for k_, v in zip([s for s, _ in steps], vals)}, round(meas, 1))
# ---------- Fig: distribusi daya dan ramp
Mx = M[(M.t >= '2026-10-17') & (M.t < '2026-10-19')].set_index('t').P_kW; day = Mx[Mx > 1]
fig, axs = plt.subplots(2, 1, figsize=(3.3, 2.9))
axs[0].hist(day, bins=np.arange(0, 135, 5), color=BL, edgecolor="white", lw=0.3); axs[0].axvline(130, color=RD, ls="--", lw=0.8)
pmx = H[(H.variant == 'base') & H.date.isin(['2026-10-17', '2026-10-18'])].P_model.max(); axs[0].axvline(pmx, color=OR, lw=0.9)
axs[0].text(128, axs[0].get_ylim()[1]*0.9, "rating\n130 kW", color=RD, fontsize=6.2, ha="right", va="top"); axs[0].text(pmx-2, axs[0].get_ylim()[1]*0.9, f"model hourly\npeak {pmx:.0f} kW", color=OR, fontsize=6.2, ha="right", va="top")
axs[0].set_xlabel("1-min AC power, daytime (kW)"); axs[0].set_ylabel("Minutes"); axs[0].text(0.02, 0.9, "(a)", transform=axs[0].transAxes)
dP = Mx.diff().abs()[Mx > 1]; axs[1].hist(dP, bins=np.arange(0, 46, 1.5), color=GR, edgecolor="white", lw=0.3); axs[1].set_yscale("log")
axs[1].set_xlabel("Change in 1-min AC power between consecutive minutes (kW)"); axs[1].set_ylabel("Minutes"); axs[1].text(0.93, 0.85, "(b)", transform=axs[1].transAxes)
plt.tight_layout(); plt.savefig(OUT+"fig_power_dist.png", dpi=300); plt.close()
print("1-min peak", Mx.max(), "99th", Mx.quantile(.99), "max step", dP.max(), "95th step", dP.quantile(.95))
# ---------- Fig: kampanye
A = H[(H.variant == 'base') & (H.P_model > 1) & (H.minutes >= 20)]
rt = A.groupby('date').apply(lambda g: (g.P_meas*g.minutes).sum()/(g.P_model*g.minutes).sum()); K2 = K.set_index('date').join(rt.rename('ratio'))
order = ['2025-06-17', '2025-08-07', '2025-10-23', '2025-10-27', '2025-12-21', '2026-02-10', '2026-04-24', '2026-10-17', '2026-10-18']; K2 = K2.loc[order]
lab = [pd.Timestamp(d).strftime('%d %b\n%y') for d in order]; x = np.arange(len(order)); col = [BL if k >= 0.9 else GR for k in K2.kt]
fig, axs = plt.subplots(2, 1, figsize=(3.3, 3.0), sharex=True)
axs[0].bar(x, K2.kt, color=col, width=0.65); axs[0].axhline(0.9, color="k", lw=0.5, ls=":"); axs[0].set_ylabel("Station GHI / clear-sky"); axs[0].set_ylim(0, 1.15); axs[0].text(0.02, 1.0, "(a)", transform=axs[0].transAxes)
axs[1].bar(x, K2.ratio, color=col, width=0.65); axs[1].axhline(1, color="k", lw=0.6); axs[1].set_ylabel("Measured / modeled"); axs[1].set_ylim(0, 1.25); axs[1].text(0.93, 0.85, "(b)", transform=axs[1].transAxes)
for xi, r in zip(x, K2.ratio): axs[1].text(xi, r+0.02, f"{r:.2f}", ha="center", fontsize=6.3)
axs[1].set_xticks(x); axs[1].set_xticklabels(lab, fontsize=6.3); plt.tight_layout(); plt.savefig(OUT+"fig_campaigns.png", dpi=300); plt.close()
K2.to_csv('outputs/validation/campaign_summary.csv'); print(K2.round(3))
