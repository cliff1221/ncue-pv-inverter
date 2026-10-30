"""Apply the author's wording edits of 31 Oct 2026 (CSME2026_Govino_A10-006_2.pdf) to content_v6.js.
Their phrasing is kept; only grammar, units, hyphenation and statements whose meaning had changed
are corrected (see the report in the conversation). Lines are replaced whole by their index pattern."""
import re

p = "content_v6.js"
L = open(p, encoding="utf8").read().split("\n")


def put(prefix, new):
    hits = [i for i, l in enumerate(L) if l.lstrip().startswith(prefix)]
    assert len(hits) == 1, (prefix, hits)
    L[hits[0]] = "  " + new


put("body(`Rooftop PV energy is often",
    "body(`Rooftop photovoltaic (PV) energy output is frequently estimated using datasheets and publicly available weather data. In this study, a 139.5 kWp PV plant in Taiwan (comprising 372 modules, one 30 kW inverter and two 50 kW inverters) is modeled using pvlib. Nine uncertain factors are ranked through a converged Sobol analysis (${N.sobol_runs.toLocaleString(\"en-US\")} runs), and the model is compared with AC power measurements at the common inverter output as well as with the lifetime energy counters of the inverters. DC loss and irradiation error account for 84% of the annual variance, while the inverter model contributes 7%. The inverter effect is primarily due to the assumed efficiency (2.6%) rather than the model structure (0.4–0.6%). On clear autumn and winter days, the plant delivered 80–89% of the modeled energy (normalized mean bias error up to +24%), although the hourly profile is accurately reproduced (correlation coefficient r ≥ 0.97). The uncertainty budget only matches the observations when all of the factors are at their minimum. Over a 3.5-year period, the inverter counters agree with the model to within 3%. The model is therefore suitable for annual energy estimates but biased at the hourly level on clear days, and on-site irradiance measurements are needed to identify the root causes.`),")

put('body("with rms values. With three wires',
    'body("With three wires and no neutral, the instantaneous power is obtained from two products (two-wattmeter method), which also applies under unbalance and distortion [28]:", { noIndent: true, keepNext: true }),')

put('caption("Fig. 2 Phase voltages',
    'caption("Fig. 2 Phase voltages of the AC bus (60 Hz): equal amplitude, displaced by 120°; 221 V rms per phase, 383 V rms line-to-line."),')

put('body("Because {i}v{/i}{sub}ab{/sub}',
    'body("Because {i}v{/i}{sub}ab{/sub} = {i}v{/i}{sub}a{/sub} − {i}v{/i}{sub}b{/sub}, a line-to-line voltage is √3 times the phase voltage and 30° ahead of it. Multiplying each current by its corresponding line-to-line voltage would therefore give 3 cos 30°/√3 = 1.5 times the true power. The voltages are 120° ± 1.5° apart, the currents lag by 0.5° to 4.3°, the unbalance is less than 3.8% and the power factor is 0.995. Eq. (1) applied to the fundamentals agrees with Eq. (2) to within 0.13% (median)."),')

put("body(`The main record (16–19 October 2026)",
    "body(`The main dataset (collected 16 to 19 October 2026) was sampled at 2 ms, thinned to 10 ms and averaged to give 4,201 one-minute values; no data gap was longer than 90 s. Seven further two-hour datasets (from 2025 to 2026) were thinned to 20 ms. Thinning without filtering introduces aliasing of the 60 Hz waveforms; however, at 10 ms and 20 ms the samples are distributed across five equally spaced points in the cycle, allowing the power ripple to average out over one minute. Sampling intervals corresponding to whole cycles, such as 200 ms, were avoided because they sample a single point in the cycle. An evaluation using ${AL.ncases} synthetic minutes (incorporating the measured unbalance, harmonics and ±30% power variation) confirmed this: the maximum error of the one-minute power was ${f2(AL.max10_free)}% for 10 ms and ${f2(AL.max20_free)}% for 20 ms intervals, and ${f2(AL.max10_locked)}% when the grid frequency was exactly 60 Hz, whereas errors reached ${f0b(AL.max200_locked)}% for 200 ms intervals.`),")

put('body("Fig. 3 shows the chain:',
    'body("Fig. 3 illustrates the sequence comprising Erbs decomposition [19], Perez transposition [20] with an albedo of 0.25, Ross cell temperature [21] and PVWatts DC power [3]:", { keepNext: true }),')

put('body("with {i}f{/i}{sub}dc{/sub} = 8.7%',
    'body("Here, {i}f{/i}{sub}dc{/sub} is set to 8.7% (or 11.4% when the default shading loss is applied). Each inverter is modeled in three ways: constant efficiency, PVWatts-DS (datasheet peak η as nominal, representing an upper bound) or PVWatts-G (η 0.96, the pvlib default); our implementation matches pvlib.inverter.pvwatts to within 0 W. A model variant incorporates the Martin–Ruiz incidence-angle loss [22], and the performance ratio is determined according to IEC 61724-1 [23].", { noIndent: true }),')

put("body(`The baseline gives 195 MWh AC",
    "body(`The baseline gives 195 MWh AC (1399 kWh/kWp), with the 5th to 95th percentile ranging from ${sgn(N.pct05[0])}% to ${sgn(N.pct05[2])}%. DC loss (−3.0% to +9.6%) and GHI error (±5%) account for 84% of the variance, and the inverter model ranks third (Fig. 4; 3% with ±10% GHI error). The total indices vary by no more than ${f3(Math.ceil(Math.max(N.conv_maxdiff05, N.conv_maxdiff10) * 1000) / 1000)} between 1,024 and 4,096 base samples, and their standard deviation across six scrambling seeds is less than 0.002. The ranking is stable from 64 samples, and the intervals for the first five factors do not overlap. Interactions are negligible (Σ{i}S{/i}{sub}T{/sub} − Σ{i}S{/i}{sub}1{/sub} = ${f3(N.interaction05)}), the layout mapping changes the energy by less than 0.01%, and no inverter clips at the baseline loss; without DC loss, clipping is limited to a maximum of 21 kWh per year.`),")

put('body("On 17 and 18 October, with 97%',
    'body("On 17 and 18 October, with 97% and 94% of clear-sky irradiation at the station, respectively, the plant produced 585 and 557 kWh (4.20 and 3.99 kWh/kWp), with a peak of 100.5 kW against the 130 kW rating (Fig. 7). The one-minute power still shows some dips (variability 0.06 and 0.13 of the mean between 10:00 and 14:00, against 0.003 on a clear February day), which the AC data alone cannot explain."),')

put('body("Across the nine days with station data',
    'body("Over the nine days with station data, {i}R{/i} ranges from 0.65 to 1.01 (Fig. 10). Only the five days above 0.9 of clear-sky irradiation are used for the bias, as a station 21 km away does not track the cloud movement over the roof; with so few records, no seasonal pattern can be separated from day-to-day differences. A single correction factor does not work either: the factor derived on 17 October (" + f3(L.k) + ") leaves a bias of " + sgn(L["2026-10-18"]) + "% on 18 October and " + sgn(L["2025-12-21"]) + "% on 21 December, but " + sgn(L["2026-02-10"]) + "% on 10 February and " + sgn(L["2025-08-07"]) + "% on 7 August. {i}R{/i} therefore cannot be used as an annual correction."),')

i = [k for k, l in enumerate(L) if l.lstrip().startswith("body(`Fig. 11 stacks the lowest end")][0]
old = L[i]
a = old.index("With isotropic transposition")
b = old.index("This joint extreme is implausible")
L[i] = old[:a] + ("With isotropic transposition (−3.9% alone) and Boland decomposition (${sgn(N.boland_alone)}%), which the earlier stack had omitted, plus PVWatts-G, a DC loss of 11.4%, NOCT 48 °C and the incidence-angle loss, the model comes down to ${f1(B[\"+ Boland decomposition\"].pct)}%; with an irradiation 5% lower it reaches ${f1(B[\"+ GHI -5 %\"].pct)}%, very close to the measured 81% ({i}R{/i} = ${f2(B[\"+ GHI -5 %\"].r17)} and ${f2(B[\"+ GHI -5 %\"].r18)}). ") + old[b:]

put('body("The data narrow the cause',
    'body("The data narrow down the cause but do not provide a definitive answer. A large bias in the station irradiation on cloud-free days is unlikely, and a fixed one-sided shadow is not supported. On the plant side, shading from the tower and frame, soiling before the rainy season, string mismatch (the 21-module string on the 30 kW inverter), de-rating of the middle inverter and short outages are all possible; on the measurement side, the uncalibrated recorder is a candidate. Separating them requires plane-of-array irradiance, inverter-level AC logging and string currents. The inverter formulations move the energy by at most 2.6% (roughly one-seventh of the gap) and give the same correlation, so the AC data alone cannot tell which is better."),')

put('body("The datasheet model gives 195 MWh',
    'body("The datasheet model gives 195 MWh (1399 kWh/kWp) per year. DC loss and irradiation error are the dominant contributors to the converged Sobol budget. The inverter effect (−2.6% to +0.4%) is an efficiency effect, not a structural one. The weather source is important at the monthly level (−12% to +19%). On clear days the plant delivered 80–89% of the modeled energy, which the budget reaches only at its joint extreme. Over the 3.5-year period the inverter counters agree with the model to within 3%. Roof-level irradiance is the next step before the inverter model is refined further."),')

open(p, "w", encoding="utf8").write("\n".join(L))
print("ok")
