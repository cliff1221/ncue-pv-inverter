import numpy as np, pandas as pd, pvlib
import config as cfg
from weather import cwa_day_file, make_location
H = pd.read_csv('outputs/validation/hourly_variants.csv')
oc = H[H.date.isin(['2026-10-17', '2026-10-18'])].copy(); oc['Pm'] = oc.P_meas.clip(lower=0)
for v in ['base', 'stack5', 'stack10']:
    print(v, [round(oc[(oc.date == d) & (oc.variant == v)].Pm.sum()/oc[(oc.date == d) & (oc.variant == v)].P_model.sum(), 3) for d in ['2026-10-17', '2026-10-18']])
f = H[(H.date == '2026-02-10') & (H.variant.isin(['base', 'stack5', 'stack10']))]
for v, g in f.groupby('variant'): print('feb10', v, round(g.P_meas.sum()/g.P_model.sum(), 3))
# kt: GHI stasiun vs langit cerah Ineichen
site = make_location()
for date, d in [('2026-10-17', 'oct2026'), ('2026-10-18', 'oct2026'), ('2026-02-10', 'new5'), ('2025-12-21', 'old2025'), ('2025-08-07', 'old2025')]:
    w = cwa_day_file(f"data/validation/codis_days/467270-{date}.csv"); cs = site.get_clearsky(w.index)
    day = cs.ghi > 50
    print(date, 'GHI stasiun harian', round(w.ghi.sum()*3.6/1000, 2), 'MJ/m2; clear-sky', round(cs.ghi.sum()*3.6/1000, 2), 'kt', round(w.ghi.sum()/cs.ghi.sum(), 3),
          'jam tengah hari (10-14) rasio', round(w.ghi[day].between(0, 2000).mean(), 2), round((w.ghi/cs.ghi)[(cs.ghi > 400)].median(), 3), 'sunshine h', round(w.sunshine_h.sum(), 1))
