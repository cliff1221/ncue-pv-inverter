"""Fig. 2 (as sketched by the supervisor): three-phase voltage waveforms, 120 deg apart,
with peak and rms values of the measured bus (line-to-line 383 V rms, 60 Hz)."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "TeX Gyre Termes", "font.size": 7, "mathtext.fontset": "stix",
                     "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False})
f = 60.0
VLL = 383.0
VPH = VLL / np.sqrt(3)            # 221 V rms
VPK = VPH * np.sqrt(2)            # 313 V peak
t = np.linspace(0, 2 / f, 2000)
ms = t * 1e3
col = {"a": "#2a6fb0", "b": "#d9822b", "c": "#3f9a5a"}

fig, ax = plt.subplots(figsize=(3.3, 2.15))
for k, sh in zip("abc", [0, -120, 120]):
    ax.plot(ms, VPK * np.sin(2 * np.pi * f * t + np.radians(sh)), color=col[k], lw=1.1, label=f"$v_{k}$")
ax.axhline(0, color="0.3", lw=0.5)
ax.axhline(VPH, color="0.45", lw=0.6, ls=(0, (3, 2)))
ax.axhline(VPK, color="0.65", lw=0.5, ls=(0, (1, 1.5)))
ax.text(33.9, VPK, f"peak\n{VPK:.0f} V", ha="left", va="center", fontsize=6.0, color="0.35", clip_on=False)
ax.text(33.9, VPH - 25, f"rms\n{VPH:.0f} V", ha="left", va="center", fontsize=6.0, color="0.35", clip_on=False)
# 120 deg shift between v_a and v_b peaks
t_a = (0.25) / f * 1e3            # peak of v_a
t_b = (0.25 + 1 / 3) / f * 1e3    # peak of v_b
ax.annotate("", xy=(t_b, VPK * 1.18), xytext=(t_a, VPK * 1.18),
            arrowprops=dict(arrowstyle="<->", lw=0.7, color="0.2", shrinkA=0, shrinkB=0))
ax.text((t_a + t_b) / 2, VPK * 1.22, "120° (5.56 ms)", ha="center", va="bottom", fontsize=6.2)
ax.set_xlim(0, 2 / f * 1e3); ax.set_ylim(-VPK * 1.12, VPK * 1.95)
ax.set_xlabel("Time (ms)"); ax.set_ylabel("Phase voltage (V)")
ax.legend(frameon=False, fontsize=6.5, ncol=3, loc="upper left", bbox_to_anchor=(0.0, 1.03), handlelength=1.4, columnspacing=1.0)
ax.text(0.995, 0.985, r"$P=\sqrt{3}\,V_{LL}\,I_{L}\cos\varphi$" "\n" r"$V_{LL}=\sqrt{3}\,V_{ph}=383$ V rms",
        transform=ax.transAxes, ha="right", va="top", fontsize=6.4,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.6", lw=0.5))
plt.tight_layout(pad=0.2, rect=[0, 0, 0.94, 1])
plt.savefig("paper_figs_rev/fig2_3phase_wave.png", dpi=500)
print("ok", round(VPH, 1), round(VPK, 1))
