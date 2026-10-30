// ================================================================ CONTENT (6-page version, figure-led)
const S = N.sobol05, S10 = N.sobol10;
const st = (k, src = S) => `${f3(src[k].ST)} ± ${f3(src[k].ST_conf)}`;
const A = N.counters, AL = N.aliasing, B = N.stack, L = N.loo;
const f0 = (x) => Math.abs((x - 1) * 100).toFixed(0);
const f0b = (x) => Number(x).toFixed(0);

const titleBlock = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 100 }, children: runs(
    "A pvlib-Based Computational Model of a Multi-Inverter Rooftop Photovoltaic Plant Driven by Public Weather Data: Sensitivity Analysis and Field Validation",
    { size: 28, bold: true }) }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: runs("Cliff Nathanael Govino{sup}*{/sup}, Wen-Ren Yang", { size: 24 }) }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: runs("International Master Program of Engineering, National Changhua University of Education,", { size: 24 }) }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: runs("Changhua, Taiwan", { size: 24 }) }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: runs("{sup}*{/sup}Email: cliffgovin@gmail.com", { size: 20 }) }),
];

const part1 = [
  sec("Abstract"),
  body(`Rooftop PV energy is often estimated from datasheets and public weather data. We model a 139.5 kWp plant in Taiwan (372 modules; one 30 kW and two 50 kW inverters) with pvlib, rank nine uncertain factors with a converged Sobol analysis (${N.sobol_runs.toLocaleString("en-US")} runs), and compare the model with the AC power recorded at the common inverter output and with the lifetime energy counters of the inverters. DC loss and irradiation error explain 84% of the annual variance and the inverter model 7%; this inverter effect comes from the assumed efficiency (2.6%) and hardly from the model structure (0.4–0.6%). On clear autumn and winter days the plant delivered 80–89% of the modeled energy (nMBE up to +24%), although the hourly profile is reproduced (r ≥ 0.97); the budget reaches this only when all factors are at their lowest ends together. Over 3.5 years, however, the inverter counters agree with the model within 3%. The model is thus suitable for annual energy but biased on clear days at hourly scale, and separating the causes requires irradiance measured on site.`),
  new Paragraph({ spacing: { before: 40 }, children: runs("{b}Keywords:{/b} Photovoltaic; Inverter modeling; pvlib; Uncertainty budget; Field validation") }),
  sec("1. Introduction"),
  body("The energy of a PV plant can be estimated from module and inverter datasheets and public weather data with pvlib [1], [2], but the result depends on the assumption made at each step. For the inverter, a constant efficiency is the simplest choice, PVWatts [3] adds a load-dependent efficiency, and the Sandia [4] and ADR [5] models need test data that datasheets rarely give; hourly data also underestimate clipping [6]. Uncertainty studies point to plane-of-array modeling [7], 2–6% annual uncertainty of satellite irradiation [8] and derate assumptions [9], but seldom treat a single rooftop plant whose weather data come from a distant station."),
  body("For the 139.5 kWp rooftop plant of National Changhua University of Education (NCUE), Taiwan, we ask: (i) how large the effect of the inverter model is compared with other factors, and whether it stems from model structure or assumed efficiency; (ii) how much the weather source (a station 21 km away or ERA5 [10]) matters; and (iii) whether the variance-based uncertainty budget [11], [12] encloses the energy the plant delivers."),
  sec("2. Plant, Data and Model"),
  sub("2.1 Plant"),
  body("The plant (24.066°N, 120.559°E) has 372 AJP-S672-375 modules [13] on open racks, facing south at 23° tilt, and feeds one 30 kW and two 50 kW inverters [14] without storage (Fig. 1, Table 1). The as-built layout found in October 2026 differs from the drawings (144/144/84 modules): 145, 140 and 87 modules in strings of 16 to 21 (Fig. 1b), which changes the annual energy by only +0.02%. Two blocks of the left inverter stand on a 7 m tower next to an empty frame of the same height, the middle inverter logs fan faults with de-rating, and the counter of the 30 kW inverter is faulty."),
];

const fig1 = [
  img("paper_figs_rev/fig1_layout.png", 6.0, { alt: "Plant layout" }),
  caption("Fig. 1 Plant layout. (a) Roof blocks and their inverter (positions schematic). (b) Strings per MPPT, AC connection and the recorder at the common AC output of the three inverters."),
];

const T1 = table([
  ["Item", "Value"],
  ["Module", "375 W, γ = −0.44 %/°C, NOCT 46 ± 2 °C"],
  ["Inverter 30 / 50 kW", "η{sub}max{/sub} 98.6 / 98.5%"],
  ["Modules (left / middle / right)", "145 / 140 / 87"],
  ["Capacity (kWp)", "54.4 / 52.5 / 32.6"],
  ["DC/AC ratio", "1.09 / 1.05 / 1.09"],
], [1800, 2565]);

const part2 = [
  tcap("Table 1 Plant data (as built)."), T1,
  sub("2.2 Weather data"),
  body("Hourly irradiation and air temperature come from the CWA Tianzhong station (467270) [15], 21.4 km from the site (1626 kWh/m² in 2023), and hourly ERA5 data from PVGIS [16], [17]. No irradiance sensor exists on the roof."),
  sub("2.3 Power measurement"),
  body("A Hioki MR8875 [18] records the three line currents and line-to-line voltages at the common AC output (Fig. 1b). The bus voltages are three sinusoids displaced by 120° (Fig. 2); for balanced conditions the active power is", { keepNext: true }),
  eq("{i}P{/i} = √3 {i}V{/i}{sub}LL{/sub} {i}I{/i}{sub}L{/sub} cos φ", 1),
  body("with rms values. With three wires and no neutral, the instantaneous power follows from two products (two-wattmeter method), which also holds under unbalance and distortion [28]:", { noIndent: true, keepNext: true }),
  eq("{i}P{/i} = ⟨{i}v{/i}{sub}ab{/sub} {i}i{/i}{sub}a{/sub} − {i}v{/i}{sub}bc{/sub} {i}i{/i}{sub}c{/sub}⟩", 2),
  img("paper_figs_rev/fig2_3phase_wave.png", 3.05, { alt: "Three-phase voltages" }),
  caption("Fig. 2 Phase voltages of the AC bus (60 Hz): equal amplitude, displaced by 120°; 221 V rms per phase, 383 V rms line-to-line."),
  body("Because {i}v{/i}{sub}ab{/sub} = {i}v{/i}{sub}a{/sub} − {i}v{/i}{sub}b{/sub}, a line-to-line voltage is √3 times the phase voltage and leads it by 30°; multiplying each current by its own line-to-line voltage would therefore overstate the power by 3 cos 30°/√3 = 1.5. The records show voltages 120° ± 1.5° apart, currents lagging by 0.5–4.3°, unbalance below 3.8% and a power factor of 0.995, and Eq. (1) applied to the fundamentals agrees with Eq. (2) within 0.13% (median)."),
  body(`The main record (16–19 October 2026) was sampled at 2 ms, thinned to 10 ms and averaged to 4,201 one-minute values; seven two-hour records (2025–2026) were thinned to 20 ms. Fig. 3 tests whether thinning biases the power, with ${AL.ncases} synthetic minutes carrying the measured unbalance, harmonics and ±30% power changes. At 10 and 20 ms the samples fall on five points of the cycle and the error stays below ${f2(AL.max10_locked)}%; intervals of whole cycles such as 200 ms err by up to ${f0b(AL.max200_locked)}% and were avoided. The chain was not calibrated; on 18 October the inverter displays showed ${f1((N.display_over_hioki - 1) * 100)}% more energy than the recorder.`),
  img("paper_figs_rev/fig_alias.png", 3.15, { alt: "Aliasing test" }),
  caption("Fig. 3 Error of the one-minute two-wattmeter power after thinning (synthetic minutes; bars: maximum)."),
  sub("2.4 Model chain"),
  body("Fig. 4 shows the chain: Erbs decomposition [19], Perez transposition [20] (albedo 0.25), Ross cell temperature [21] and PVWatts DC power [3],", { keepNext: true }),
  eq("{i}P{/i}{sub}dc{/sub} = {i}P{/i}{sub}0{/sub}({i}G{/i}/1000)[1 + γ({i}T{/i}{sub}c{/sub} − 25)](1 − {i}f{/i}{sub}dc{/sub})", 3),
  body("with {i}f{/i}{sub}dc{/sub} = 8.7%. Each inverter is modeled with constant efficiency, PVWatts-DS (datasheet peak η as nominal, an upper bound) or PVWatts-G (η 0.96); our code equals pvlib.inverter.pvwatts to 0 W. A variant adds the Martin–Ruiz incidence-angle loss [22]; the performance ratio follows IEC 61724-1 [23].", { noIndent: true }),
  img("paper_figs_rev/fig_chain.png", 3.15, { alt: "Model chain" }),
  caption("Fig. 4 Model chain. Grey: alternatives varied in Section 3 (e.g. Faiman [24] and SAPM [25] cell temperature)."),
  sec("3. Annual Uncertainty Budget"),
  body("Nine factors were varied with SALib [26] (Table 2): continuous factors uniformly over the stated ranges, model options with equal weight. The ranges are assumptions with the given basis, and the ranking depends on them, as the ±5% and ±10% GHI cases show."),
];

const T2 = table([
  ["Factor", "Range, distribution and basis", "{i}S{/i}{sub}T{/sub} (±5% GHI)", "{i}S{/i}{sub}T{/sub} (±10% GHI)"],
  ["DC loss", "0–11.4%, uniform; PVWatts total loss without / with shading [3]", st("rugi_DC"), st("rugi_DC", S10)],
  ["GHI error", "±5% (±10%), uniform; pyranometer class and 21 km distance [8]", st("galat_GHI"), st("galat_GHI", S10)],
  ["Inverter model", "constant η, PVWatts-DS, PVWatts-G; equal weight", st("model_inverter"), st("model_inverter", S10)],
  ["Transposition", "Perez, isotropic, Klucher, Hay-Davies, Reindl; equal weight", st("transposisi"), st("transposisi", S10)],
  ["Cell temperature", "Ross, Faiman, SAPM; equal weight", st("model_suhu_sel"), st("model_suhu_sel", S10)],
  ["Decomposition", "Erbs, disc, Boland, Orgill-Hollands; equal weight", st("dekomposisi_GHI"), st("dekomposisi_GHI", S10)],
  ["NOCT", "44–48 °C, uniform; datasheet 46 ± 2 °C", st("NOCT"), st("NOCT", S10)],
  ["Time shift", "−0.5, 0, +0.5 h; meaning of the hour label", st("geser_waktu"), st("geser_waktu", S10)],
  ["Mapping", "two layouts that satisfy the inverter limits", st("pemetaan"), st("pemetaan", S10)],
], [1500, 4770, 1400, 1400], { size: 16 });

const table2 = [
  tcap("Table 2 Factors, ranges and Sobol total index {i}S{/i}{sub}T{/sub} (4,096 base samples, 95% bootstrap interval)."),
  T2, new Paragraph({ spacing: { after: 60 }, children: [] }),
];

const M = N.metrics;
const mrow = (d, lab) => { const r = M[d]; return [lab, `${r.hours}`, f2(r.ratio), sgn(r.MBE_kW), sgn(r.nMBE_pct, 0), f1(r.RMSE_kW), f1(r.nRMSE_pct), (r.r === null || r.hours < 5) ? "–" : f2(r.r)]; };
const T3 = table([
  ["Record", "h", "{i}R{/i}", "MBE (kW)", "nMBE (%)", "RMSE (kW)", "nRMSE (%)", "{i}r{/i}"],
  mrow("2026-10-17", "17 Oct 26"), mrow("2026-10-18", "18 Oct 26"), mrow("2026-02-10", "10 Feb 26"),
  mrow("2025-12-21", "21 Dec 25"), mrow("2025-08-07", "7 Aug 25"),
], [830, 260, 470, 590, 560, 590, 590, 475], { size: 15 });

const part3 = [
  sub("3.1 Results and convergence"),
  body(`The baseline gives 195 MWh AC (1399 kWh/kWp), and the 5th–95th percentile spans ${sgn(N.pct05[0])}% to ${sgn(N.pct05[2])}%. DC loss (−3.0% to +9.6%) and GHI error (±5%) explain 84% of the variance and the inverter model ranks third (Fig. 5a). The total indices change by less than ${f3(Math.max(N.conv_maxdiff05, N.conv_maxdiff10))} between 1,024 and 4,096 base samples, five other seeds differ by at most ${f3(N.seed_sd05)}, and the ranking is stable from 64 samples (Fig. 5b); the intervals of the first five factors do not overlap. Interactions are negligible (Σ{i}S{/i}{sub}T{/sub} − Σ{i}S{/i}{sub}1{/sub} = ${f3(N.interaction05)}), and no inverter clips at the baseline loss.`),
  img("paper_figs_rev/fig_sobol2.png", 3.2, { alt: "OAT and Sobol convergence" }),
  caption("Fig. 5 (a) Change in annual energy when one factor moves within its range (orange: lowest, blue: highest) and {i}S{/i}{sub}T{/sub}. (b) {i}S{/i}{sub}T{/sub} against base samples with 95% interval."),
  sub("3.2 Inverter: structure or efficiency"),
  body("The formulations differ in curve shape and in assumed efficiency at once. Fig. 6 separates the two: at equal η, constant efficiency and PVWatts differ by 0.36–0.63%, whereas lowering η from 0.985 to 0.96 removes 2.6%. The inverter share of the budget is therefore an efficiency assumption, not a structural effect."),
  img("paper_figs_rev/fig_inv.png", 3.1, { alt: "Inverter structure vs efficiency" }),
  caption("Fig. 6 Annual energy relative to PVWatts-DS for both structures at equal efficiency (as-built layout, 2023)."),
  sub("3.3 Weather source"),
  body("Station and ERA5 irradiation differ by +2.6% mean bias and 37% RMSE (r = 0.83). The annual energy changes by +3.4%, but the monthly energy by −12% to +19% (Fig. 7), so at monthly scale the weather source outweighs the inverter model."),
  img("paper_figs/fig_hourly.png", 3.05, { alt: "Monthly energy station vs ERA5" }),
  caption("Fig. 7 Monthly AC energy driven by station or ERA5 irradiation (2023)."),
];

const part4 = [
  sec("4. Field Validation"),
  sub("4.1 Measured output"),
  body("On 17 and 18 October, with 97% and 94% of clear-sky irradiation at the station, the plant produced 585 and 557 kWh (4.20 and 3.99 kWh/kWp), with a peak of 100.5 kW against the 130 kW rating (Fig. 8). The one-minute power still shows dips (variability 0.06 and 0.13 of the mean between 10:00 and 14:00, against 0.003 on a clear February day) that AC data alone cannot attribute."),
  img("paper_figs/fig_meas3d.png", 2.9, { alt: "Measured power 16-19 Oct" }),
  caption("Fig. 8 Measured AC power, 16–19 October 2026 (one-minute means)."),
  sub("4.2 Model against measurement"),
  body("Agreement is expressed by the ratio", { keepNext: true }),
  eq("{i}R{/i} = Σ{i}P{/i}{sub}actual{/sub} / Σ{i}P{/i}{sub}model{/sub}", 4),
  body(`over the hours of a record ({i}R{/i} < 1: model too high) and by the mean bias and RMS errors normalized by the mean measured power (Table 3). The hourly shape is reproduced, but the model is higher in almost every hour (Fig. 9): {i}R{/i} = 0.81 with nMBE +23% and +24% on 17 and 18 October, and 0.80 on 19 October; the performance ratio is 0.63 measured against 0.78 modeled. The hourly ratio stays near 0.8 from morning to afternoon (morning/afternoon 0.82/0.80 and 0.76/0.86; Fig. 10), so a one-sided obstruction is unlikely. A factor fitted on 17 October leaves biases of ${sgn(L["2026-02-10"])}% and ${sgn(L["2025-08-07"])}% on 10 February and 7 August, so {i}R{/i} must not be used as a correction.`, { noIndent: true }),
  img("paper_figs_rev/fig_modelvs_rev.png", 3.0, { alt: "Hourly measured vs modeled" }),
  caption("Fig. 9 Hourly AC power, measured and modeled; the band reaches the stacked lower bounds of Section 4.4."),
  tcap("Table 3 Error metrics on clear-sky records (hours ≥ 20 min, weighted; {i}r{/i} for full days)."), T3,
  img("paper_figs/fig_ratio_hour.png", 3.0, { alt: "Ratio by hour" }),
  caption("Fig. 10 Measured over modeled hourly power on the clear-sky records."),
  sub("4.3 Other records"),
  body("Across the nine days with station data, {i}R{/i} lies between 0.65 and 1.01 (Fig. 11). Only the five days above 0.9 of clear-sky irradiation are used for the bias, because a station 21 km away does not follow the clouds over the roof; with so few records a seasonal pattern cannot be separated from day-to-day differences."),
  img("paper_figs/fig_campaigns.png", 2.9, { alt: "Clear-sky fraction and ratio per record" }),
  caption("Fig. 11 (a) Clear-sky fraction of the station irradiation and (b) {i}R{/i} per record; blue: fraction above 0.9."),
  sub("4.4 Closing the budget"),
  body(`Fig. 12 stacks the lowest end of every factor. With isotropic transposition (−3.9% alone) and Boland decomposition (${sgn(N.boland_alone)}%), which the earlier stack omitted, the model reaches ${f1(B["+ GHI -5 %"].pct)}% of the baseline, close to the measured 81%. This joint extreme is implausible: the isotropic model underestimates tilted irradiance under clear skies [27], the combination lowers the annual energy by ${f1(-N.annual_all_lowest)}% against a 5th percentile of ${sgn(N.pct05[0])}%, and on 10 February it underestimates the measurement by ${f0(B["+ GHI -5 %"].rfeb)}%.`),
  img("paper_figs_rev/fig_closure_rev.png", 3.0, { alt: "Stacked lower bounds" }),
  caption("Fig. 12 Modeled energy of 17–18 October with the lower ends stacked; orange: added in this revision; red: measured."),
  sub("4.5 Long-term check"),
  body(`The lifetime counters of the two 50 kW inverters (${A.left.kwh.toLocaleString("en-US")} and ${A.middle.kwh.toLocaleString("en-US")} kWh after 1280 days) exceed the model for the same calendar period by ${f1((A.left.ratio - 1) * 100)}% and ${f1((A.middle.ratio - 1) * 100)}% (${Math.round(A.left.y_cnt)} and ${Math.round(A.middle.y_cnt)} against 1399 kWh/kWp per year; Fig. 13), although they read 3% above the recorder and the weather of 2024–2026 is not modeled. A permanent 19% loss would have shown, so the clear-day bias is condition-specific. Candidate causes are shading by the tower and frame, soiling, string mismatch, de-rating of the middle inverter and the uncalibrated recorder; the inverter formulations (≤ 2.6%) explain about a seventh of the gap.`),
  img("paper_figs_rev/fig_longterm.png", 3.05, { alt: "Clear days vs counters" }),
  caption("Fig. 13 Measured over modeled energy: clear-day records and 3.5-year inverter counters."),
];

const part5 = [
  sec("5. Discussion and Limitations"),
  body(`The model is suitable for annual energy, within the budget of ${sgn(N.pct05[0])}% to ${sgn(N.pct05[2])}%, but not for hourly prediction on clear days, where it is about 20% too high. (1) The field data are three days and seven two-hour records, mostly autumn and winter, and two uncalibrated counters; utility meter data and a year of logging would allow a seasonal check. (2) Without irradiance on the roof the error cannot be split into an irradiance and a plant part; this is the main gap. (3) Only the combined AC output was measured. (4) The ranking depends on the assigned ranges.`),
  sec("6. Conclusions"),
  body("The datasheet model gives 195 MWh (1399 kWh/kWp) per year. DC loss and irradiation error dominate the converged Sobol budget, and the inverter effect (−2.6% to +0.4%) is an efficiency assumption rather than a structural one. The weather source matters at monthly scale (−12% to +19%). On clear days the plant produced 80–89% of the modeled energy, reached by the budget only at its joint extreme, while over 3.5 years the inverter counters agree within 3%. Roof-level irradiance is the next step before the inverter model is refined further."),
  sec("Data Availability"),
  body("Code and data: https://github.com/cliff1221/ncue-pv-inverter.", { noIndent: true }),
  sec("References"),
];
