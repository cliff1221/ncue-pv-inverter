"""Fig. 2 (new): three-wire connection of the recorder and phasor diagram.
Angles: phase sequence a-b-c; measured displacement angle 0.5-4.3 deg (drawn at 10 deg so that it is
visible; marked in the figure)."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc

plt.rcParams.update({"font.family": "TeX Gyre Termes", "font.size": 6.5, "mathtext.fontset": "stix"})
fig = plt.figure(figsize=(3.45, 2.3))

# ---------------- (a) wiring
ax = fig.add_axes([0.0, 0.0, 0.53, 1.0]); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
ax.text(1, 97, "(a) Connection (three-wire)", fontsize=7, weight="bold", va="top")
Y = {"a": 74, "b": 56, "c": 38}
for k, y in Y.items():
    ax.plot([4, 97], [y, y], color="0.15", lw=1.0)
    ax.text(3, y, k, ha="right", va="center", fontsize=7, style="italic")
    ax.add_patch(Circle((22, y), 4.2, fill=False, ec="#b33a3a", lw=0.9))
    ax.text(22, y + 6.0, {"a": "CH1-1", "b": "CH1-2", "c": "CH1-3"}[k], ha="center", fontsize=5.6, color="#b33a3a")
ax.annotate("", xy=(97, 84), xytext=(76, 84), arrowprops=dict(arrowstyle="-|>", lw=0.6))
ax.text(86.5, 86.5, "to grid", ha="center", fontsize=5.8)
ax.text(5, 87, "from inverters", fontsize=5.8)
# voltage channels between lines
def vch(x, k1, k2, name):
    y1, y2 = Y[k1], Y[k2]
    ax.plot([x, x], [y1, y2], color="#3b6fb6", lw=0.7)
    ax.plot([x], [y1], "o", ms=2.2, color="#3b6fb6"); ax.plot([x], [y2], "o", ms=2.2, color="#3b6fb6")
    yc = (y1 + y2) / 2
    ax.add_patch(Rectangle((x - 5.5, yc - 3.2), 11, 6.4, fc="white", ec="#3b6fb6", lw=0.7, zorder=5))
    ax.text(x, yc, name, ha="center", va="center", fontsize=5.4, color="#3b6fb6", zorder=6)
vch(42, "a", "b", "$v_{ab}$")
vch(58, "b", "c", "$v_{bc}$")
# c-a lead drawn on the side
ax.plot([75, 75], [Y["a"], Y["c"]], color="#3b6fb6", lw=0.7)
ax.plot([75], [Y["a"]], "o", ms=2.2, color="#3b6fb6"); ax.plot([75], [Y["c"]], "o", ms=2.2, color="#3b6fb6")
ax.add_patch(Rectangle((69.5, 43.8), 11, 6.4, fc="white", ec="#3b6fb6", lw=0.7, zorder=5))
ax.text(75, 47, "$v_{ca}$", ha="center", va="center", fontsize=5.4, color="#3b6fb6", zorder=6)
ax.text(50, 29.5, "CH2-1, CH2-2, CH2-3: line-to-line", ha="center", fontsize=5.6, color="#3b6fb6")
ax.text(2, 20.5, "No neutral: $i_a + i_b + i_c = 0$, so two products\nsuffice (two-wattmeter, Aron):",
        fontsize=5.8, va="top", linespacing=1.2)
ax.text(50, 7.5, r"$P = \langle v_{ab}\, i_a - v_{bc}\, i_c \rangle$", ha="center", fontsize=7.5)

# ---------------- (b) phasors
bx = fig.add_axes([0.53, 0.0, 0.47, 1.0]); bx.set_xlim(-1.35, 1.35); bx.set_ylim(-2.05, 1.55)
bx.set_aspect("equal"); bx.axis("off")
bx.text(-1.33, 1.52, "(b) Phasors (sequence a-b-c)", fontsize=7, weight="bold", va="top")
def arrow(ang, r, col, lw=0.9, ls="-", label=None, lr=1.12, fs=6.3):
    x, y = r * np.cos(np.radians(ang)), r * np.sin(np.radians(ang))
    bx.annotate("", xy=(x, y), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", lw=lw, color=col, ls=ls, mutation_scale=6))
    if label:
        bx.text(lr * x, lr * y, label, ha="center", va="center", fontsize=fs, color=col)
rp, rl, ri = 0.62, 0.62 * np.sqrt(3) * 0.62, 0.48
rl = 0.92
for ang, lab in [(0, "$V_a$"), (-120, "$V_b$"), (120, "$V_c$")]:
    arrow(ang, rp, "0.55", lw=0.7, ls=(0, (2, 1.5)), label=lab, lr=1.25, fs=5.8)
for ang, lab in [(30, "$V_{ab}$"), (150, "$V_{ca}$")]:
    arrow(ang, rl, "#3b6fb6", lw=1.0, label=lab, lr=1.15)
arrow(-90, rl, "#3b6fb6", lw=1.0)
bx.text(0.17, -0.86, "$V_{bc}$", fontsize=6.3, color="#3b6fb6", va="center")
phi = 10
for ang, lab in [(-phi, "$I_a$"), (-120 - phi, "$I_b$"), (120 - phi, "$I_c$")]:
    arrow(ang, ri, "#b33a3a", lw=1.0, label=lab, lr=1.28, fs=5.8)
arrow(90, rl, "#3b6fb6", lw=0.6, ls=(0, (1, 1)))
bx.text(0.08, 0.86, "$V_{cb} = -V_{bc}$", fontsize=5.6, color="#3b6fb6", va="center")
bx.add_patch(Arc((0, 0), 0.5, 0.5, theta1=-phi, theta2=30, color="0.2", lw=0.6))
bx.text(0.43, 0.115, r"$30°{+}\varphi$", fontsize=5.0, ha="left", va="center")
bx.text(-1.33, -1.6, r"$P = V_{ab}I_a\cos(30°{+}\varphi) + V_{cb}I_c\cos(30°{-}\varphi)$" "\n"
        r"$\;\;\, = \sqrt{3}\,V_{LL} I \cos\varphi$;  $\varphi$ measured 0.5–4.3° (drawn 10°)" "\n"
        r"$\Sigma\, v_{LL} i$ gives $3V_{LL}I\cos 30° \approx 1.5\,P$",
        fontsize=5.3, va="center", linespacing=1.35)
fig.savefig("paper_figs_rev/fig2_3phase.png", dpi=500)
print("ok")
