"""Compact figures for the 6-page revision (one column wide, about 3.3 x 1.9 in).
  fig_alias.png     error of one-minute power vs thinning interval (synthetic test)
  fig_chain.png     model chain, horizontal
  fig_sobol2.png    (a) one-at-a-time range, (b) Sobol convergence with 95% CI
  fig_inv.png       inverter: structure vs assumed efficiency
  fig_longterm.png  measured/model: clear-day records vs 3.5-year inverter counters
Run from repo root after rev_analysis.py, rev_aliasing.py, rev_sobol_convergence.py."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams.update({"font.family": "TeX Gyre Termes", "font.size": 7, "mathtext.fontset": "stix",
                     "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False})
BL, OR, GR, RD, GY = "#2a6fb0", "#d9822b", "#3f9a5a", "#c0392b", "#8a8a8a"
OUT = "paper_figs_rev/"

# ------------------------------------------------------------------ aliasing
D = pd.read_csv("outputs/rev/aliasing_mc.csv")
cols = ["2 ms (raw)", "10 ms (thin-out 5, Oct 2026)", "20 ms (2025-26 records)", "200 ms (thin-out 100, avoided)"]
lab = ["2 ms\n(raw)", "10 ms\n(Oct 2026)", "20 ms\n(2025–26)", "200 ms\n(avoided)"]
fig, ax = plt.subplots(figsize=(3.3, 1.85))
rng = np.random.default_rng(1)
for i, c in enumerate(cols):
    for st, col, dx, name in [("f 59.95-60.05 Hz", BL, -0.13, "grid 59.95–60.05 Hz"), ("f = 60.000 Hz (locked)", OR, 0.13, "grid exactly 60 Hz")]:
        v = D[D.set == st][c].abs().clip(lower=1e-6)
        ax.scatter(i + dx + rng.uniform(-0.06, 0.06, len(v)), v, s=2.5, color=col, alpha=0.55, lw=0,
                   label=name if i == 0 else None)
        ax.plot([i + dx - 0.1, i + dx + 0.1], [v.max()] * 2, color=col, lw=1.0)
ax.set_yscale("log"); ax.set_ylim(1e-6, 60)
ax.axhline(0.5, color="0.4", lw=0.6, ls=(0, (3, 2))); ax.text(-0.45, 0.6, "0.5 %", fontsize=6, va="bottom", ha="left", color="0.3")
ax.set_xticks(range(4)); ax.set_xticklabels(lab, fontsize=6.5); ax.set_xlim(-0.5, 3.5)
ax.set_ylabel("|error| of 1-min power (%)")
ax.legend(frameon=False, fontsize=6, loc="upper left", bbox_to_anchor=(0.0, 1.02), markerscale=3, handletextpad=0.2)
plt.tight_layout(pad=0.2); plt.savefig(OUT + "fig_alias.png", dpi=450); plt.close()

# ------------------------------------------------------------------ model chain
fig = plt.figure(figsize=(3.3, 1.95)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 60); ax.axis("off")
steps = [("Weather", "GHI, $T_{air}$ (CODiS)", "ERA5; GHI ±5 % (±10 %)"),
         ("GHI → DNI, DHI", "Erbs", "disc, Boland, Orgill-H."),
         ("Transposition", "Perez, 23°", "isotropic, Klucher,\nHay-Davies, Reindl"),
         ("Cell temperature", "Ross, NOCT 46 °C", "Faiman, SAPM;\nNOCT 44–48 °C"),
         ("DC power", "PVWatts, loss 8.7 %", "loss 0–11.4 %"),
         ("Inverter ×3", "PVWatts-DS", "constant η, PVWatts-G;\nmapping a / b"),
         ("AC energy", "sum, hourly → kWh", "time stamp ±0.5 h")]
W, H = 21.5, 11.5
pos = [(1, 44), (26, 44), (51, 44), (76, 44), (14, 16), (39, 16), (64, 16)]
for (t, d, alt), (x, y) in zip(steps, pos):
    fc = "#f6e3c8" if t.startswith("Inverter") else ("0.93" if t in ("Weather", "AC energy") else "#eef3f8")
    ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle="round,pad=0.3", fc=fc, ec="0.45", lw=0.6))
    ax.text(x + W / 2, y + 8.3, t, ha="center", va="center", fontsize=6.0, weight="bold")
    ax.text(x + W / 2, y + 3.4, d, ha="center", va="center", fontsize=5.4)
    ax.text(x + W / 2, y - 1.6, alt, ha="center", va="top", fontsize=5.0, color="0.38", linespacing=1.05)
for (x1, y1), (x2, y2) in zip(pos[:3], pos[1:4]):
    ax.annotate("", xy=(x2 - 0.4, y2 + H / 2), xytext=(x1 + W + 0.4, y1 + H / 2), arrowprops=dict(arrowstyle="-|>", lw=0.6, mutation_scale=5))
ax.annotate("", xy=(pos[4][0] + W / 2, pos[4][1] + H + 0.4), xytext=(pos[3][0] + W / 2, pos[3][1] - 8.5),
            arrowprops=dict(arrowstyle="-|>", lw=0.6, mutation_scale=5, connectionstyle="angle,angleA=-90,angleB=180,rad=0"))
for (x1, y1), (x2, y2) in zip(pos[4:6], pos[5:7]):
    ax.annotate("", xy=(x2 - 0.4, y2 + H / 2), xytext=(x1 + W + 0.4, y1 + H / 2), arrowprops=dict(arrowstyle="-|>", lw=0.6, mutation_scale=5))
ax.text(50, 1.0, "black: baseline;  grey: alternatives varied in the uncertainty budget", ha="center", fontsize=5.3, color="0.35")
plt.savefig(OUT + "fig_chain.png", dpi=450); plt.close()

# ------------------------------------------------------------------ Sobol: OAT + convergence
O = pd.read_csv("outputs/yr05_sens_oat.csv")
Cv = pd.read_csv("outputs/rev05_conv.csv")
name = {"rugi_DC": "DC loss", "galat_GHI": "GHI error", "model_inverter": "Inverter model", "transposisi": "Transposition",
        "model_suhu_sel": "Cell temp.", "dekomposisi_GHI": "Decomposition", "NOCT": "NOCT", "geser_waktu": "Time shift", "pemetaan": "Mapping"}
order = ["rugi_DC", "galat_GHI", "model_inverter", "transposisi", "model_suhu_sel", "dekomposisi_GHI", "NOCT", "geser_waktu", "pemetaan"]
fin = Cv[(Cv.seed == 7) & (Cv.N == 4096)].set_index("factor")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(3.35, 2.0), gridspec_kw=dict(width_ratios=[1.15, 1]))
y = np.arange(len(order))[::-1]
for yi, f in zip(y, order):
    g = O[O.faktor == f].selisih_persen
    a1.barh(yi, g.min(), color=OR, height=0.6); a1.barh(yi, g.max(), color=BL, height=0.6)
    a1.text(11.5, yi, f"{fin.loc[f, 'ST']:.2f}", va="center", fontsize=5.8)
a1.axvline(0, color="0.2", lw=0.5)
a1.set_yticks(y); a1.set_yticklabels([name[f] for f in order], fontsize=6)
a1.set_xlim(-6, 14); a1.set_xlabel("Δ annual energy (%)", fontsize=6.5)
a1.text(11.5, len(order) - 0.35, "$S_T$", fontsize=6.2, ha="left")
a1.set_title("(a) one at a time", fontsize=6.8, loc="left")
top = ["rugi_DC", "galat_GHI", "model_inverter", "transposisi", "model_suhu_sel"]
cc = [BL, OR, RD, GR, GY]
s7 = Cv[Cv.seed == 7]
for f, c in zip(top, cc):
    g = s7[s7.factor == f].sort_values("N")
    a2.plot(g.N, g.ST, color=c, lw=0.9, marker="o", ms=1.8, label={"model_inverter": "Inverter", "transposisi": "Transp."}.get(f, name[f]))
    a2.fill_between(g.N, g.ST - g.ST_conf, g.ST + g.ST_conf, color=c, alpha=0.18, lw=0)
a2.set_xscale("log", base=2); a2.set_xticks([64, 256, 1024, 4096]); a2.set_xticklabels(["64", "256", "1024", "4096"], fontsize=6)
a2.set_xlabel("base samples $N$", fontsize=6.5); a2.set_ylabel("$S_T$ (95 % CI)", fontsize=6.5); a2.set_ylim(0, 0.75)
a2.legend(frameon=False, fontsize=5.3, loc="center right", bbox_to_anchor=(1.02, 0.235), ncol=2, handlelength=1.0, columnspacing=0.6, handletextpad=0.3)
a2.set_title("(b) convergence", fontsize=6.8, loc="left")
plt.tight_layout(pad=0.25, w_pad=0.6); plt.savefig(OUT + "fig_sobol2.png", dpi=450); plt.close()

# ------------------------------------------------------------------ inverter structure vs efficiency
A = pd.read_csv("outputs/rev/A_structure_vs_eta_annual.csv").set_index("case").d_pct
grp = [("η = 0.96", "constant eta = 0.96", "PVWatts eta_nom = 0.96"),
       ("η = 0.98", "constant eta = 0.98", "PVWatts eta_nom = 0.98"),
       ("η = 0.985", "constant eta = 0.985", "PVWatts eta_nom = 0.985"),
       ("same peak\n(98.5/98.6 %)", "constant eta = datasheet peak", "PVWatts, peak of curve = datasheet peak")]
fig, ax = plt.subplots(figsize=(3.3, 1.8))
x = np.arange(len(grp))
c1 = [A[g[1]] for g in grp]; c2 = [A[g[2]] for g in grp]
ax.bar(x - 0.18, c1, 0.34, color=BL, label="constant efficiency")
ax.bar(x + 0.18, c2, 0.34, color=OR, label="PVWatts curve")
for xi, a, b in zip(x, c1, c2):
    ax.text(xi - 0.18, a + (0.08 if a >= 0 else -0.08), f"{a:+.2f}", ha="center", va="bottom" if a >= 0 else "top", fontsize=5.6)
    ax.text(xi + 0.18, b + (0.08 if b >= 0 else -0.08), f"{b:+.2f}", ha="center", va="bottom" if b >= 0 else "top", fontsize=5.6)
ax.axhline(0, color="0.2", lw=0.5)
ax.set_xticks(x); ax.set_xticklabels([g[0] for g in grp], fontsize=6.3)
ax.set_ylabel("Δ annual energy (%)"); ax.set_ylim(-3.2, 1.3); ax.set_xlim(-0.5, 3.6)
ax.text(3.55, -1.55, "same η, constant vs PVWatts:\n0.36–0.63 % (structure)\nPVWatts, η 0.985 → 0.96:\n−2.6 % (efficiency)",
        fontsize=5.7, color="0.2", ha="right", va="top", linespacing=1.2)
ax.legend(frameon=False, fontsize=6, loc="upper left", ncol=2, bbox_to_anchor=(0.0, 1.05))
plt.tight_layout(pad=0.2); plt.savefig(OUT + "fig_inv.png", dpi=450); plt.close()

# ------------------------------------------------------------------ long-term vs clear days
Cm = pd.read_csv("outputs/rev/C_metrics.csv")
Dc = pd.read_csv("outputs/rev/D_counters.csv")
labs = {"2026-10-17": "17 Oct 2026", "2026-10-18": "18 Oct 2026", "2026-02-10": "10 Feb 2026", "2025-12-21": "21 Dec 2025", "2025-08-07": "7 Aug 2025"}
rows = [(labs[r.date], r.ratio, BL) for r in Cm.itertuples()]
rows += [(f"{r.inverter} 50 kW, 3.5 yr", r.counter_over_model_same_period, GR) for r in Dc.itertuples()]
fig, ax = plt.subplots(figsize=(3.3, 1.75))
yy = np.r_[np.arange(5)[::-1] + 2.6, np.arange(2)[::-1]]
for yi, (l, v, c) in zip(yy, rows):
    ax.barh(yi, v, color=c, height=0.62); ax.text(v + 0.01, yi, f"{v:.2f}", va="center", fontsize=5.9)
ax.axvline(1.0, color="0.2", lw=0.7)
ax.set_yticks(yy); ax.set_yticklabels([r[0] for r in rows], fontsize=6.2)
ax.set_xlim(0.6, 1.12); ax.set_xlabel("measured / modeled energy")
ax.text(0.61, yy[0] + 0.55, "clear-day records (recorder, hourly)", fontsize=5.8, color=BL, va="bottom")
ax.text(0.61, yy[-2] + 0.55, "lifetime inverter counters", fontsize=5.8, color=GR, va="bottom")
ax.set_ylim(-0.6, yy[0] + 1.3)
plt.tight_layout(pad=0.2); plt.savefig(OUT + "fig_longterm.png", dpi=450); plt.close()
print("ok")
