"""Switching-level model of a three-phase two-level PWM inverter (the same circuit as the
MATLAB File Exchange model 44676 "3 phase inverter": six-switch bridge, sine-triangle PWM
with optional 3rd-harmonic injection), with this plant's numbers:
  DC link 700 V (MPPT voltages read on the displays: 560-750 V),
  grid 383 V rms line-to-line, 60 Hz, carrier 16 kHz (typical for string inverters),
  L filter + grid voltage, 50 kW inverter at full power (76 A rms rated AC current).
Output: paper_figs_rev/fig_inverter_pwm.png and printed numbers.
Not a model of the CyberPower control firmware (unknown); it shows how the bridge turns DC into
the three-phase AC that the Hioki measured."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

plt.rcParams.update({"font.family": "TeX Gyre Termes", "font.size": 7, "mathtext.fontset": "stix",
                     "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False})
COL = {"a": "#2a6fb0", "b": "#d9822b", "c": "#3f9a5a"}

VDC, F, FC = 700.0, 60.0, 16000.0
VLL = 383.0
VPH_PK = VLL / np.sqrt(3) * np.sqrt(2)          # grid phase peak, 312.7 V
P_OUT = 50e3
I_PK = P_OUT / (3 * VLL / np.sqrt(3)) * np.sqrt(2)   # 106.6 A peak (75.4 A rms)
L = 0.6e-3                                      # filter inductance per phase
W = 2 * np.pi * F
# inverter fundamental needed: V_inv = V_grid + j w L I  (unity power factor)
v_drop = W * L * I_PK
V_INV_PK = np.hypot(VPH_PK, v_drop)
DELTA = np.arctan2(v_drop, VPH_PK)
THI = True
m = V_INV_PK / (VDC / 2)                        # modulation index (phase peak / (Vdc/2))
print(f"I_pk {I_PK:.1f} A, inverter phase peak {V_INV_PK:.1f} V, m = {m:.3f} "
      f"(SPWM limit 1.000, with 3rd harmonic 1.155)")

dt = 1 / (FC * 200)
t = np.arange(0, 3 / F, dt)
ph = {"a": 0.0, "b": -2 * np.pi / 3, "c": 2 * np.pi / 3}
ref = {k: m * np.sin(W * t + DELTA + p) for k, p in ph.items()}
if THI:
    third = -m / 6 * np.sin(3 * (W * t + DELTA))
    ref = {k: r + third for k, r in ref.items()}
car = 2 * np.abs(2 * ((t * FC) % 1) - 1) - 1        # triangle -1..1
leg = {k: np.where(ref[k] >= car, VDC / 2, -VDC / 2) for k in ph}   # leg voltage vs DC midpoint
vn = (leg["a"] + leg["b"] + leg["c"]) / 3                             # neutral shift (3-wire)
vgrid = {k: VPH_PK * np.sin(W * t + p) for k, p in ph.items()}
# integrate L di/dt = v_leg - v_n - v_grid (start at steady state)
i = {k: np.zeros_like(t) for k in ph}
for k, p in ph.items():
    i0 = I_PK * np.sin(p)
    i[k] = i0 + np.cumsum(leg[k] - vn - vgrid[k]) * dt / L
    # remove the integration drift (DC offset) using the last two cycles
    n = int(round(1 / F / dt))
    i[k] -= i[k][n:].mean()
vab = leg["a"] - leg["b"]

# fundamental of v_ab and THD of current (last two cycles)
n = int(round(1 / F / dt)); sl = slice(n, None)
def fund(x):
    tt = t[sl]; c = 2 * np.mean(x[sl] * np.cos(W * tt)); s = 2 * np.mean(x[sl] * np.sin(W * tt))
    return np.hypot(c, s)
vab1 = fund(vab)
ia1 = fund(i["a"])
ia_rms = np.sqrt(np.mean(i["a"][sl] ** 2))
thd_i = np.sqrt(max(ia_rms ** 2 - (ia1 / np.sqrt(2)) ** 2, 0)) / (ia1 / np.sqrt(2)) * 100
P = 3 * np.mean(np.array([vgrid[k][sl] * i[k][sl] for k in ph]).sum(0)) / 3
print(f"v_ab fundamental {vab1/np.sqrt(2):.1f} V rms (grid {VLL} V), i_a {ia1/np.sqrt(2):.1f} A rms, "
      f"current THD {thd_i:.1f} %, P = {P/1e3:.1f} kW")

# ------------------------------------------------------------------ figure
fig = plt.figure(figsize=(3.35, 4.9))
gs = fig.add_gridspec(4, 1, height_ratios=[1.25, 1, 1, 1], hspace=0.75)

# (a) circuit
ax = fig.add_subplot(gs[0]); ax.set_xlim(0, 100); ax.set_ylim(0, 50); ax.axis("off")
ax.set_title("(a) Two-level bridge: PV DC link to 3-wire AC grid", fontsize=7, loc="left", pad=2)
TOP, BOT = 44, 6
ax.plot([10, 66], [TOP, TOP], color="0.2", lw=0.8); ax.plot([10, 66], [BOT, BOT], color="0.2", lw=0.8)
ax.plot([10, 10], [BOT, TOP], color="0.2", lw=0.8)
ax.add_patch(Rectangle((4, 18), 12, 14, fc="#f6e3c8", ec="0.3", lw=0.6, zorder=3))
ax.text(10, 25, "PV\n700 V", ha="center", va="center", fontsize=5.6, zorder=4)
ax.plot([22, 22], [TOP, 27], color="0.2", lw=0.6); ax.plot([22, 22], [23, BOT], color="0.2", lw=0.6)
ax.plot([19, 25], [27, 27], color="0.2", lw=1.0); ax.plot([19, 25], [23, 23], color="0.2", lw=1.0)
ax.text(26.5, 25, "C", fontsize=6, va="center")
for j, (k, x) in enumerate(zip("abc", [36, 49, 62])):
    for y0, lab in [(31, f"S{j+1}"), (12, f"S{j+4}")]:
        ax.add_patch(Rectangle((x - 2.5, y0), 5, 7, fc="white", ec=COL[k], lw=0.8, zorder=3))
        ax.text(x - 3.4, y0 + 3.5, lab, fontsize=5.0, va="center", ha="right")
    ax.plot([x, x], [BOT, TOP], color="0.2", lw=0.6, zorder=1)
    ax.plot([x], [25], "o", ms=2.6, color=COL[k], zorder=4)
    ax.plot([x, x + 4.2], [25, 25], color=COL[k], lw=0.9, zorder=2)
    ax.text(x + 4.8, 25, k, fontsize=6.6, va="center", style="italic", color=COL[k])
# filter + grid block
for j, k in enumerate("abc"):
    yy = 35 - j * 10
    ax.text(72.5, yy, k, fontsize=6.6, va="center", ha="right", style="italic", color=COL[k])
    ax.plot([73.5, 77], [yy, yy], color=COL[k], lw=0.9)
    ax.add_patch(Rectangle((77, yy - 2), 7, 4, fc="white", ec=COL[k], lw=0.8)); ax.text(80.5, yy, "L", fontsize=5.4, ha="center", va="center")
    ax.plot([84, 88], [yy, yy], color=COL[k], lw=0.9)
ax.add_patch(Rectangle((88, 12), 11, 26, fc="0.94", ec="0.4", lw=0.6))
ax.text(93.5, 25, "grid\n383 V\n60 Hz", fontsize=5.4, ha="center", va="center")

# (b) PWM references and carrier
ax = fig.add_subplot(gs[1]); ms = t * 1e3
zoom = (t >= 0) & (t < 1 / F)
car_slow = 2 * np.abs(2 * ((t * 900) % 1) - 1) - 1   # carrier drawn at 900 Hz so it is visible
for k in ph:
    ax.plot(ms[zoom], ref[k][zoom], color=COL[k], lw=0.9, label=f"ref {k}")
ax.plot(ms[zoom], car_slow[zoom], color="0.6", lw=0.4, label="carrier (drawn 0.9 kHz)")
ax.set_ylim(-1.25, 1.25); ax.set_ylabel("p.u.")
ax.set_title(f"(b) Sine-triangle PWM with 3rd-harmonic injection, m = {m:.2f}", fontsize=7, loc="left", pad=11)
ax.legend(frameon=False, fontsize=5, ncol=4, loc="lower center", bbox_to_anchor=(0.5, 0.96), handlelength=1.2, columnspacing=0.8)

# (c) line voltage pulses and fundamental
ax = fig.add_subplot(gs[2])
ax.plot(ms[zoom], vab[zoom], color="0.75", lw=0.3, label="$v_{ab}$ (switched)")
tt = t[zoom]
ax.plot(ms[zoom], np.sqrt(2) * vab1 / np.sqrt(2) * np.sin(W * tt + DELTA + np.pi / 6 + np.angle(1)), color=COL["a"], lw=1.0, label="fundamental")
ax.set_ylabel("V"); ax.set_ylim(-800, 800)
ax.set_title(f"(c) Line voltage: ±{VDC:.0f} V pulses, fundamental {vab1/np.sqrt(2):.0f} V rms", fontsize=7, loc="left", pad=11)
ax.legend(frameon=False, fontsize=5.2, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 0.96), handlelength=1.2)

# (d) phase currents
ax = fig.add_subplot(gs[3])
for k in ph:
    ax.plot(ms[zoom], i[k][zoom], color=COL[k], lw=0.8, label=f"$i_{k}$")
ax.set_ylabel("A"); ax.set_xlabel("Time (ms)")
ax.set_title(f"(d) Phase currents at 50 kW: {ia1/np.sqrt(2):.0f} A rms, 120° apart, THD {thd_i:.1f} %", fontsize=7, loc="left", pad=11)
ax.legend(frameon=False, fontsize=5.2, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 0.96), handlelength=1.2)
fig.savefig("paper_figs_rev/fig_inverter_pwm.png", dpi=450, bbox_inches="tight", pad_inches=0.03)
print("ok")
