"""Fig. 1 (revised): rooftop blocks, strings, inverters and Hioki measurement point.
Block sizes and string lengths: as-built survey of 18 Oct 2026 (drawing sheet 8/9 annotations,
module count per block, inverter LCD string currents and MPPT voltages).
Block positions on the roof are schematic (not to scale)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
import os

plt.rcParams.update({"font.family": "TeX Gyre Termes", "font.size": 7, "mathtext.fontset": "stix"})
C = {"L": "#3b6fb6", "M": "#e08a2c", "R": "#3f9a5a"}
LF = {"L": "#dbe6f5", "M": "#fbe6cf", "R": "#d9efdf"}

fig = plt.figure(figsize=(7.0, 3.55))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 200); ax.set_ylim(0, 101); ax.axis("off")

MW, MH = 1.45, 1.75   # module drawn size


def block(x0, y0, rows, colfn, label, sub=None, hatch=None):
    """rows: list of row lengths (top to bottom). colfn(row, col) -> inverter key."""
    for r, n in enumerate(rows):
        for c in range(n):
            k = colfn(r, c)
            ax.add_patch(Rectangle((x0 + c * MW, y0 - (r + 1) * MH), MW * 0.9, MH * 0.85,
                                   fc=LF[k], ec=C[k], lw=0.35, hatch=hatch))
    ax.text(x0, y0 + 1.2, label, ha="left", va="bottom", fontsize=7, weight="bold")
    if sub:
        ax.text(x0, y0 - len(rows) * MH - 1.0, sub, ha="left", va="top", fontsize=6.2, color="0.25")


# ---------------- (a) roof
ax.text(1, 99, "(a) Rooftop array (schematic, not to scale)", fontsize=8, weight="bold", va="top")
block(3, 88, [23] * 7, lambda r, c: "R" if c < 3 else "M", "Block 161",
      "7 rows: cols 1-3 = one 21-module string (30 kW);\ncols 4-23 = 7 strings of 20 (middle 50 kW)")
block(3, 56, [16] * 7, lambda r, c: "L", "Block 112", "7 strings of 16 (left 50 kW)")
block(34, 56, [17, 16], lambda r, c: "L", "Block 33", "17 + 16, on a tower\nabout 7 m high (left 50 kW)")
ax.add_patch(Rectangle((33, 34.5), 27.5, 7.5, fill=False, ec="0.35", lw=0.8, ls=(0, (3, 2))))
ax.text(46.7, 33.6, "empty steel frame, 7 m high\n(marked as shading on drawing)", ha="center", va="top", fontsize=6.2, color="0.25")
block(3, 25, [16, 16, 16, 18], lambda r, c: "R", "Block 66", "3 strings of 16 + 1 of 18 (30 kW)")
ax.annotate("", xy=(4, 2.5), xytext=(4, 9.5), arrowprops=dict(arrowstyle="-|>", lw=0.8, color="0.2"))
ax.text(5.5, 6, "modules face south (tilt 23°)", fontsize=6.2, va="center")
for k, t, y in [("L", "left 50 kW", 23), ("M", "middle 50 kW", 19), ("R", "right 30 kW", 15)]:
    ax.add_patch(Rectangle((40, y - 1), 2.6, 2.2, fc=LF[k], ec=C[k], lw=0.6)); ax.text(43.5, y + 0.1, t, va="center", fontsize=6.4)
ax.plot([63.5, 63.5], [2, 99], color="0.75", lw=0.6)

# ---------------- (b) single line
ax.text(65.5, 99, "(b) Strings, inverters and measurement point", fontsize=8, weight="bold", va="top")
INV = [("L", "Left inverter 50 kW", "CPSPV50000ETL-WB", ["A: 3 strings", "B: 3 strings", "C: 3 strings"],
        "145 modules\n54.4 kWp\n8 × 16 + 1 × 17", "XLPE 50 mm²\nMCCB 125 A"),
       ("M", "Middle inverter 50 kW", "CPSPV50000ETL-WB", ["A: 3 × 20", "B: 2 × 20", "C: 2 × 20"],
        "140 modules\n52.5 kWp\n7 × 20", "XLPE 50 mm²\nMCCB 125 A"),
       ("R", "Right inverter 30 kW", "CPSPV30000ETLA-WB", ["A: 2 × 16", "B: 16 and 18*", "C: 1 × 21"],
        "87 modules\n32.6 kWp\n3 × 16 + 18 + 21", "XLPE 14 mm²\nMCCB 60 A")]
ys = [80, 53, 26]
bus_x = 137
for (k, name, model, mppt, mods, cab), y in zip(INV, ys):
    ax.add_patch(FancyBboxPatch((66, y - 9), 20, 18, boxstyle="round,pad=0.3", fc=LF[k], ec=C[k], lw=0.8))
    ax.text(76, y + 5.3, "PV array", ha="center", fontsize=6.6, weight="bold")
    ax.text(76, y - 1.6, mods, ha="center", va="center", fontsize=6.2, linespacing=1.2)
    ax.add_patch(FancyBboxPatch((93, y - 9), 28, 18, boxstyle="round,pad=0.3", fc="white", ec=C[k], lw=1.0))
    ax.text(107, y + 5.8, name, ha="center", fontsize=6.6, weight="bold")
    ax.text(107, y + 2.7, model, ha="center", fontsize=5.8, color="0.3")
    for i, m in enumerate(mppt):
        ax.text(95, y - 1.2 - i * 2.9, "MPPT " + m, fontsize=6.1)
        ax.annotate("", xy=(93, y - 0.4 - i * 2.9), xytext=(86.6, y - 0.4 - i * 2.9),
                    arrowprops=dict(arrowstyle="-|>", lw=0.5, color=C[k], mutation_scale=5))
    ax.text(89.8, y + 3.3, "DC", ha="center", fontsize=5.8, color="0.35")
    ax.plot([121.3, bus_x], [y, y], color="0.15", lw=1.0)
    ax.text(129, y + 0.9, cab, ha="center", va="bottom", fontsize=5.3, color="0.3", linespacing=1.1)
ax.text(93, 14.5, "* 16- and 18-module strings in parallel on one MPPT", fontsize=5.6, color="0.3")
# AC panel bus
ax.plot([bus_x, bus_x], [ys[-1], ys[0]], color="0.15", lw=2.2)
ax.text(bus_x, ys[0] + 6.5, "AC panel\n3φ 380 V", ha="center", fontsize=6.4, weight="bold")
ax.plot([bus_x, 146], [53, 53], color="0.15", lw=1.4)
ax.text(141.5, 49.2, "225 A", ha="center", fontsize=5.6, color="0.3")
# Hioki
HX = 149
ax.add_patch(Circle((HX, 53), 2.8, fc="#fbe3e3", ec="#b33a3a", lw=1.0))
ax.text(HX, 53, "H", ha="center", va="center", fontsize=6.5, weight="bold", color="#b33a3a")
ax.add_patch(FancyBboxPatch((142, 63), 37.5, 15, boxstyle="round,pad=0.4", fc="#fdf1f1", ec="#b33a3a", lw=0.8))
ax.text(160.7, 76.4, "Hioki MR8875 recorder", ha="center", va="top", fontsize=6.7, weight="bold", color="#b33a3a")
ax.text(143.2, 72.7, "CH1-1..1-3: clamps on $i_a$, $i_b$, $i_c$\nCH2-1..2-3: $v_{ab}$, $v_{bc}$, $v_{ca}$\n2 ms sampling, two-wattmeter power",
        va="top", fontsize=5.9, linespacing=1.25)
ax.plot([HX, HX], [55.8, 62.6], color="#b33a3a", lw=0.7, ls=(0, (2, 1.5)))
ax.text(HX, 48.5, "measured:\nsum of the\nthree inverters", ha="center", va="top", fontsize=5.8, color="#b33a3a", style="italic")
# to grid
ax.plot([151.8, 199], [53, 53], color="0.15", lw=1.4)
ax.add_patch(FancyBboxPatch((158.3, 22), 40.4, 18, boxstyle="round,pad=0.3", fc="0.95", ec="0.4", lw=0.7))
ax.text(179, 37.8, "Grid connection", ha="center", va="top", fontsize=6.6, weight="bold")
ax.text(159.4, 33.8, "50 m XLPE 125 mm² → sale meter (MB)\n→ 35 m → building bus MPA (B3F)\nTR#A 1500 kVA, 380 V / 11.4 kV\n"
        "capacitor bank 440 kvar on same bus", va="top", fontsize=5.7, linespacing=1.22)
ax.annotate("", xy=(179, 40.6), xytext=(179, 53), arrowprops=dict(arrowstyle="-|>", lw=0.8, color="0.2"))
ax.text(159.4, 15.5, "Full feed-in, no battery. Only the AC sum\nwas recorded; per-inverter and DC values\nwere read from the inverter displays.",
        va="top", fontsize=5.7, color="0.3", linespacing=1.22)

os.makedirs("paper_figs_rev", exist_ok=True)
fig.savefig("paper_figs_rev/fig1_layout.png", dpi=400)
print("ok")
