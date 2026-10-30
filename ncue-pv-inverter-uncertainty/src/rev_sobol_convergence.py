"""Reviewer point 4: Sobol convergence and confidence intervals.

Runs Saltelli/Sobol sampling with N = 4096 base samples (45,056 runs) for the
same nine factors and ranges as run_sens_year.py. Because the scrambled Sobol
sequence is nested, the first n*(D+2) rows form the design for N = n, so the
indices for N = 64 ... 4096 come from one set of runs. Five extra scrambling
seeds at N = 1024 show the seed-to-seed spread.

Usage:  GHI_ERR=0.05 OUTP=rev05 python src/rev_sobol_convergence.py
Output: outputs/{OUTP}_conv.csv  (factor, N, seed, S1, S1_conf, ST, ST_conf)
"""
import os, sys, time
import numpy as np, pandas as pd
from SALib.sample import sobol as ssample
from SALib.analyze import sobol as sanalyze
import sens_year as sens

P = os.environ.get("OUTP", "rev05")
F, B = sens.FACTORS, sens.BASE
names = list(F)
D = len(names)
problem = dict(num_vars=D, names=names, bounds=[[0, 1]] * D)


def decode(u):
    p = dict(B)
    for n, v in zip(names, u):
        kind, spec = F[n]
        if kind == "cat":
            p[n] = spec[min(int(v * len(spec)), len(spec) - 1)]
        else:
            p[n] = spec[0] + v * (spec[1] - spec[0])
    return p


def run_design(X):
    E = np.empty(len(X))
    for i, u in enumerate(X):
        E[i] = sens.run(decode(u))[0]
    return E


rows = []


def analyse(E, n, seed):
    Si = sanalyze.analyze(problem, E[: n * (D + 2)], calc_second_order=False,
                          num_resamples=1000, conf_level=0.95, seed=1, print_to_console=False)
    for k, nm in enumerate(names):
        rows.append(dict(factor=nm, N=n, seed=seed, S1=Si["S1"][k], S1_conf=Si["S1_conf"][k],
                         ST=Si["ST"][k], ST_conf=Si["ST_conf"][k]))


NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
t0 = time.time()
X = ssample.sample(problem, NMAX, calc_second_order=False, seed=7)
E = run_design(X)
np.save(f"outputs/{P}_conv_E.npy", E)
print(f"N={NMAX}: {len(X)} runs in {time.time() - t0:.0f} s"); sys.stdout.flush()
n = 64
while n <= NMAX:
    analyse(E, n, 7)
    n *= 2
# percentile range of the annual energy from the A and B matrices (pure random draws)
idx = np.r_[np.arange(0, len(E), D + 2), np.arange(D + 1, len(E), D + 2)]
e0 = sens.run(B)[0]
q = np.percentile(E[idx] / e0 - 1, [5, 50, 95]) * 100
print("5/50/95 percentile vs baseline (%):", np.round(q, 2))

for seed in [11, 23, 37, 51, 89]:
    Xs = ssample.sample(problem, 1024, calc_second_order=False, seed=seed)
    analyse(run_design(Xs), 1024, seed)
    print("seed", seed, "done", f"{time.time() - t0:.0f} s"); sys.stdout.flush()

out = pd.DataFrame(rows)
out.to_csv(f"outputs/{P}_conv.csv", index=False)
print(out[out.seed == 7].pivot(index="factor", columns="N", values="ST").round(3).to_string())
