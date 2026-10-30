"""Reviewer point 3: does thinning the Hioki samples (2 ms -> 10 ms or 20 ms) bias the
one-minute two-wattmeter (Aron) active power?

The raw 2 ms waveforms are not in the repository, so the test uses synthetic three-wire
signals built from the measured characteristics of this plant (Section 2.2):
  line-to-line voltage 383 V, frequency 59.95-60.05 Hz, plus a set locked at exactly 60.000 Hz (worst case),
  voltage and current unbalance up to 3.8 % and 3.6 % (maximum measured),
  displacement angle 0-5 deg (measured -0.5 to -4.3 deg),
  odd harmonics 5, 7, 11, 13 with random phase (amplitudes typical of string inverters,
  current THD about 4 %, voltage THD about 2.7 %; deliberately on the high side),
  and a power change of up to +-30 % within the minute (cloud edge).
For each of 300 random cases the 60 s mean of p(t) = v_ab i_a - v_bc i_c is computed
from a 0.1 ms reference grid and from sample trains with dt = 2, 10, 20 and 200 ms that start
at a random instant (the recorder clock is not locked to the grid).
Output: outputs/rev/aliasing_mc.csv, outputs/rev/aliasing_summary.csv
"""
import os
import numpy as np, pandas as pd

rng = np.random.default_rng(2026)
os.makedirs("outputs/rev", exist_ok=True)
T = 60.0                       # averaging window (s)
DT_REF = 1e-4                 # 10 kHz reference, far above the highest ripple (~1.6 kHz)
DTS = {"2 ms (raw)": 2e-3, "10 ms (thin-out 5, Oct 2026)": 10e-3, "20 ms (2025-26 records)": 20e-3,
       "200 ms (thin-out 100, avoided)": 200e-3}
VLL = 383.0
VPH = VLL / np.sqrt(3) * np.sqrt(2)          # phase peak
I1 = 150.0 * np.sqrt(2)                      # ~ 100 kW
HV = {5: 0.020, 7: 0.015, 11: 0.008, 13: 0.006}      # voltage harmonics (fraction of fundamental)
HI = {5: 0.030, 7: 0.020, 11: 0.012, 13: 0.010}      # current harmonics
SEQ = {1: 1, 5: -1, 7: 1, 11: -1, 13: 1}             # natural sequence of each harmonic


def phase_set(amp, h, ang, unb, unb_ang):
    """Three phase signals (a,b,c) of harmonic h: main sequence + small opposite sequence."""
    s = SEQ[h]
    out = []
    for k in range(3):
        main = amp * np.exp(1j * (ang - s * 2 * np.pi * k / 3))
        opp = amp * unb * np.exp(1j * (unb_ang + s * 2 * np.pi * k / 3))
        out.append(main + opp)
    return out          # complex amplitudes (no zero sequence -> three-wire)


def case(f_fixed=None):
    f = rng.uniform(59.95, 60.05) if f_fixed is None else f_fixed
    uv, ui = rng.uniform(0, 0.038), rng.uniform(0, 0.036)
    phi = np.radians(rng.uniform(0, 5))
    V = {1: phase_set(VPH, 1, 0.0, uv, rng.uniform(0, 2 * np.pi))}
    I = {1: phase_set(I1, 1, -phi, ui, rng.uniform(0, 2 * np.pi))}
    for h in HV:
        V[h] = phase_set(VPH * HV[h], h, rng.uniform(0, 2 * np.pi), rng.uniform(0, 0.05), rng.uniform(0, 2 * np.pi))
        I[h] = phase_set(I1 * HI[h], h, rng.uniform(0, 2 * np.pi), rng.uniform(0, 0.05), rng.uniform(0, 2 * np.pi))
    ramp = rng.uniform(-0.3, 0.3)            # linear power change over the minute
    wob = rng.uniform(0, 0.1); fw = rng.uniform(0.05, 2.0)   # slow wobble

    def p_of_t(t):
        env = (1 + ramp * (t / T - 0.5)) * (1 + wob * np.sin(2 * np.pi * fw * t))
        va = sum((V[h][0] * np.exp(1j * 2 * np.pi * h * f * t)).real for h in V)
        vb = sum((V[h][1] * np.exp(1j * 2 * np.pi * h * f * t)).real for h in V)
        vc = sum((V[h][2] * np.exp(1j * 2 * np.pi * h * f * t)).real for h in V)
        ia = env * sum((I[h][0] * np.exp(1j * 2 * np.pi * h * f * t)).real for h in I)
        ic = env * sum((I[h][2] * np.exp(1j * 2 * np.pi * h * f * t)).real for h in I)
        return (va - vb) * ia - (vb - vc) * ic

    tr = np.arange(0, T, DT_REF)
    pref = p_of_t(tr)
    Pref = pref.mean()
    row = dict(f=f, uv=uv, ui=ui, ripple_pct=pref.std() / Pref * 100, P_kW=Pref / 1e3)
    for name, dt in DTS.items():
        t0 = rng.uniform(0, dt)
        ts = np.arange(t0, T, dt)
        row[name] = (p_of_t(ts).mean() / Pref - 1) * 100
    return row


rows = [dict(case(), set="f 59.95-60.05 Hz") for _ in range(300)] + \
       [dict(case(60.0), set="f = 60.000 Hz (locked)") for _ in range(100)]
D = pd.DataFrame(rows)
D.to_csv("outputs/rev/aliasing_mc.csv", index=False)
S = pd.concat({st: pd.DataFrame({n: dict(mean_pct=g[n].mean(), p99_abs_pct=g[n].abs().quantile(0.99),
                                         max_abs_pct=g[n].abs().max()) for n in DTS}).T
               for st, g in D.groupby("set")})
S.to_csv("outputs/rev/aliasing_summary.csv")
print("ripple of p(t) (std/mean, %): median", round(D.ripple_pct.median(), 2), "max", round(D.ripple_pct.max(), 2))
print(S.round(4).to_string())
