"""Revised Fig. 6: band from baseline down to the full lower-bound stack (all factors at their lowest)."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "serif", "font.serif": ["Liberation Serif", "Times New Roman"], "font.size": 7.5,
                     "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False})
BL = "#2a7ab0"
D = pd.read_csv("outputs/rev/hourly_base_stack_oct.csv")
fig, axs = plt.subplots(2, 1, figsize=(3.3, 3.15), sharex=True)
for ax, d, lab in zip(axs, ["2026-10-17", "2026-10-18"], ["(a) 17 Oct 2026", "(b) 18 Oct 2026"]):
    g = D[D.date == d].set_index("hour"); h = np.arange(5, 20)
    ax.fill_between(h, g.P_stack.reindex(h).fillna(0), g.P_base.reindex(h).fillna(0), color="#b7d3e8", lw=0,
                    label="model, all lower bounds stacked")
    ax.plot(h, g.P_base.reindex(h).fillna(0), color=BL, lw=1.0, label="model baseline")
    ax.plot(h, g.P_meas.clip(lower=0).reindex(h).fillna(0), color="k", lw=1.0, marker="o", ms=2.5, label="measured (Hioki)")
    ax.set_ylabel("AC power (kW)"); ax.text(0.02, 0.9, lab, transform=ax.transAxes, fontsize=7)
h_, l_ = axs[0].get_legend_handles_labels()
fig.legend([h_[2], h_[1], h_[0]], [l_[2], l_[1], l_[0]], loc="lower center", ncol=3, frameon=False, fontsize=5.8,
           handlelength=1.4, columnspacing=0.8)
axs[1].set_xlabel("Hour label (end of hour, UTC+8)")
plt.tight_layout(rect=[0, 0.06, 1, 1]); plt.savefig("paper_figs_rev/fig_modelvs_rev.png", dpi=400)
