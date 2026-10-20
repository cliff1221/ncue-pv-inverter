"""Ringkas CSV Hioki (hasil Wave Viewer) menjadi satu tabel daya per menit.

Pemakaian paling mudah: taruh skrip ini DI FOLDER yang berisi CSV, lalu jalankan
(tombol Run di VS Code juga bisa):
    python summarize_hioki.py
Hasil: hasil_ringkasan.csv di folder yang sama.

Atau dengan folder lain:
    python summarize_hioki.py FOLDER_CSV hasil_ringkasan.csv

FOLDER_CSV = folder berisi file .csv hasil konversi Wave Viewer
             (kanal: CH1-1..1-3 arus [A], CH2-1..2-3 tegangan antar-fasa [V]).
Butuh: Python 3 + pandas + numpy  (pip install pandas numpy)
"""
import sys, glob, os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

WIN = 60.0  # detik per baris ringkasan


def read_one(path):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        lines = []
        for n, line in enumerate(fh):
            lines.append(line)
            if line.startswith('"Time'):
                break
            if n > 60:
                raise ValueError("header 'Time' tidak ditemukan")
    # baris di bawah judul "Shot": shot, time/div, tanggal picu, jam picu
    import csv
    rows_h = list(csv.reader(lines))
    k = next(j for j, r in enumerate(rows_h) if r and r[0] == "Shot") + 1
    trig = datetime.strptime(rows_h[k][2] + " " + rows_h[k][3], "%y-%m-%d %H:%M:%S.%f")
    d = pd.read_csv(path, skiprows=n + 1, header=None,
                    names=["t", "i1", "i2", "i3", "v1", "v2", "v3"]).dropna()
    return trig, d


def summarize(path):
    trig, d = read_one(path)
    out = []
    d["w"] = (d["t"] // WIN).astype(int)
    for w, s in d.groupby("w"):
        if len(s) < 50:
            continue
        i = [np.sqrt((s[c] ** 2).mean()) for c in ("i1", "i2", "i3")]
        v = [np.sqrt((s[c] ** 2).mean()) for c in ("v1", "v2", "v3")]
        # dua wattmeter (tegangan antar-fasa, 3 kawat); rata-rata 3 kombinasi
        pa = (s.v1 * s.i1 - s.v2 * s.i3).mean()
        pb = (s.v2 * s.i2 - s.v3 * s.i1).mean()
        pc = (s.v3 * s.i3 - s.v1 * s.i2).mean()
        p = (pa + pb + pc) / 3.0
        iavg, vavg = float(np.mean(i)), float(np.mean(v))
        sapp = np.sqrt(3) * iavg * vavg
        out.append({
            "waktu_mulai": (trig + timedelta(seconds=float(w * WIN))).strftime("%Y-%m-%d %H:%M:%S"),
            "P_kW": round(p / 1e3, 3),
            "I_rms_A": round(iavg, 2),
            "V_rms_V": round(vavg, 1),
            "pf": round(p / sapp, 3) if sapp > 50 else np.nan,
            "n_sampel": len(s),
            "file": os.path.basename(path),
        })
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    folder = sys.argv[1] if len(sys.argv) > 1 else here
    outpath = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "hasil_ringkasan.csv")
    files = [f for f in sorted(glob.glob(os.path.join(folder, "*.csv")))
             if os.path.basename(f).lower() != "hasil_ringkasan.csv"
             and os.path.abspath(f) != os.path.abspath(outpath)]
    if not files:
        print("Tidak ada file .csv di", folder)
        sys.exit(1)
    print("Folder:", folder, "|", len(files), "file CSV")
    rows = []
    for k, f in enumerate(files, 1):
        try:
            rows += summarize(f)
        except Exception as e:  # file rusak/terpotong: lewati, catat
            print("LEWATI", os.path.basename(f), "->", e)
        if k % 20 == 0:
            print(k, "/", len(files))
    df = pd.DataFrame(rows).sort_values("waktu_mulai")
    df.to_csv(outpath, index=False)
    print("Selesai:", len(df), "baris ->", outpath)


if __name__ == "__main__":
    main()
