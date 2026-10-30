"""Revised budget-closure figure: every factor at its lowest setting, stacked.
Reads outputs/rev/B_lower_bound_stack.csv (rev_analysis.py)."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "TeX Gyre Termes", "font.size": 6.8})
B = pd.read_csv("outputs/rev/B_lower_bound_stack.csv")
H = pd.read_csv("outputs/validation/hourly_variants.csv")
oc = H[H.date.isin(["2026-10-17", "2026-10-18"]) & (H.variant == "base")]
meas = oc.P_meas.clip(lower=0).sum() / oc.P_model.sum() * 100
lab = {"baseline": "Baseline model", "+ PVWatts-G": "+ PVWatts-G inverter", "+ DC loss 11.4 %": "+ DC loss 11.4 %",
       "+ NOCT 48": "+ NOCT 48 °C", "+ IAM (Martin-Ruiz)": "+ incidence-angle loss", "+ isotropic transposition": "+ isotropic transposition",
       "+ Boland decomposition": "+ Boland decomposition", "+ GHI -5 %": "+ GHI −5 %", "+ GHI -10 % (instead of -5 %)": "GHI −10 % instead of −5 %"}
vals = B.model_pct_oct.values; names = [lab[s] for s in B.step]
col = ["#2a6fb0"] + ["#8fb8d6"] * 4 + ["#e3a35c"] * 2 + ["#8fb8d6", "#d5dee6"]
fig, ax = plt.subplots(figsize=(3.35, 2.45)); y = np.arange(len(vals))[::-1]
ax.barh(y, vals, color=col, height=0.62)
for yi, v in zip(y, vals): ax.text(v + 0.5, yi, f"{v:.1f}", va="center", fontsize=6.3)
ax.axvline(meas, color="#c0392b", lw=1.1); ax.text(meas - 0.5, -1.05, f"measured {meas:.0f} %", color="#c0392b", fontsize=6.5, ha="right", va="center")
ax.set_yticks(y); ax.set_yticklabels(names, fontsize=6.4); ax.set_xlim(70, 108); ax.set_ylim(-1.5, len(vals) - 0.4)
ax.set_xlabel("Modeled energy, 17–18 Oct 2026 (% of baseline)")
ax.spines[["top", "right"]].set_visible(False)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="#8fb8d6", label="in the earlier stack"), Patch(color="#e3a35c", label="added in this revision")],
          frameon=False, fontsize=6.0, loc="lower right", bbox_to_anchor=(1.02, 0.02))
plt.tight_layout(); plt.savefig("paper_figs_rev/fig_closure_rev.png", dpi=400); print("measured %", round(meas, 2))
