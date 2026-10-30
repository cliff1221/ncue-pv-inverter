// Response to the supervisor's review. Build: node paper_rev/build_response.js
const fs = require("fs"), path = require("path");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, BorderStyle, ShadingType, VerticalAlign } = require("docx");
const N = JSON.parse(fs.readFileSync(path.join(__dirname, "numbers.json"), "utf8"));
const FONT = "Times New Roman";
const f1 = (x) => Number(x).toFixed(1), f2 = (x) => Number(x).toFixed(2), f3 = (x) => Number(x).toFixed(3);
const sg = (x, d = 1) => (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(d);
const P = (t, o = {}) => new Paragraph({ spacing: { after: o.after ?? 80 }, alignment: o.align, children: [new TextRun({ text: t, font: FONT, size: o.size || 21, bold: o.bold, italics: o.italics })] });
const B = { style: BorderStyle.SINGLE, size: 4, color: "999999" };
const cell = (t, w, o = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA }, borders: { top: B, bottom: B, left: B, right: B },
  shading: o.head ? { type: ShadingType.CLEAR, fill: "E8EEF4", color: "auto" } : undefined,
  margins: { top: 60, bottom: 60, left: 90, right: 90 }, verticalAlign: VerticalAlign.TOP,
  children: (Array.isArray(t) ? t : [t]).map((x) => new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: x, font: FONT, size: 19, bold: o.head })] })),
});
const W = [2700, 4900, 1760];
const rows = [
  ["Reviewer comment", "Response and change", "Where"],
  ["1. Empirical validation is insufficient (about three months of data and a few short records).",
   ["Agreed; the field data remain limited and this is now stated as limitation (1). The raw Hioki recording did not run continuously, so no further measured days exist.",
    `Added a long-term check that needs no new measurement: the lifetime energy counters of the two 50 kW inverters (1280 days since commissioning). Compared with the model for the same calendar period, the counters are ${f1((N.counters.left.ratio - 1) * 100)}% and ${f1((N.counters.middle.ratio - 1) * 100)}% higher (${Math.round(N.counters.left.y_cnt)} and ${Math.round(N.counters.middle.y_cnt)} vs 1399 kWh/kWp/yr). The counters read about ${f1((N.display_over_hioki - 1) * 100)}% above the recorder (checked on 18 Oct 2026). Conclusion changed: the 19% clear-day shortfall is not a permanent loss; the model is suitable for annual energy but not for hourly prediction on clear days.`,
    "Suggested future data: monthly kWh of the Taipower sale meter and continuous logging."], "Abstract; 4.5; Fig. 12; 5; 6"],
  ["2. Irradiance from a station 21 km away; no on-site measurement, so discrepancies cannot be attributed to plant losses.",
   ["Agreed. No pyranometer exists on the roof, so this cannot be fixed with present data. The paper now says explicitly that the model error cannot be split into an irradiance part and a plant part, and names a plane-of-array pyranometer or reference cell as the most important next step.",
    "Mitigation already in the paper: only days with station clear-sky fraction > 0.9 are used for the bias; the hour-by-hour pattern and the February/October contrast argue against a constant station bias."], "2.2; 4.6; 5 (2)"],
  ["3. Measurement layout is not shown; thinning 2 ms → 10 ms must be validated for aliasing of the active power.",
   ["New Fig. 1: roof blocks, strings per MPPT, the three inverters, AC panel, recorder position and grid connection.",
    "New Fig. 2 (as sketched by the supervisor): three phase voltages of the bus, 120° apart, with rms and peak values; Eq. (1) P = √3·V_LL·I_L·cos φ and Eq. (2) two-wattmeter power. Text explains why Σ v_LL·i would give 1.5 P.",
    `Aliasing (Section 2.3): explained why the mean power is preserved (samples at five equally spaced phases; whole-cycle intervals avoided) and tested with ${N.aliasing.ncases} synthetic minutes built from the measured unbalance, displacement and harmonics. Max error ${f2(N.aliasing.max10_free)}% (10 ms) and ${f2(N.aliasing.max20_free)}% (20 ms); ${f2(N.aliasing.max10_locked)}% and ${f2(N.aliasing.max20_locked)}% even at exactly 60 Hz; 200 ms would err by up to ${Number(N.aliasing.max200_locked).toFixed(0)}%.`,
    "Note: the raw 2 ms files are not kept; if any are found, the same test can be repeated on real data with src/rev_aliasing.py adapted."], "Fig. 1; Fig. 2; 2.3"],
  ["4. Sobol ranking depends on ranges and distributions; show convergence, convergence testing and confidence intervals.",
   ["Table 2 now gives the range, distribution and basis of every factor and states that the ranking depends on them (the ±10% GHI case shows the shift).",
    `Convergence (Section 3.1): base samples raised from 1,024 to 4,096 (${N.sobol_runs.toLocaleString("en-US")} runs) plus five extra scrambling seeds. Total indices change by at most ${f3(N.conv_maxdiff05)} (±5%) and ${f3(N.conv_maxdiff10)} (±10%); seed-to-seed SD ≤ ${f3(N.seed_sd05)}; top-five ranking stable from ${N.rank_stable_from} samples. Table 2 reports S_T with 95% bootstrap confidence intervals; the last four factors have indices below 0.005 and are not ranked.`], "3 and 3.1; Table 2; Fig. 4"],
  ["5. Distinguish differences in model structure from differences in assumed rated efficiency.",
   [`New Section 3.2 and Fig. 5. Same η: constant vs PVWatts differ by 0.36–0.37%; same peak efficiency: 0.6%; changing η from 0.985 to 0.96 within PVWatts: −2.6%. So the inverter effect in the budget is an efficiency assumption, not a structural one. On the clear October days the two structures with equal η differ by < 0.1%.`], "3.2; Fig. 5; Abstract; 6"],
  ["6. Clarify the 'stacked lower-bound assumption' and why options that would give lower output were excluded.",
   [`The reviewer is right: the earlier stack left out isotropic transposition (−3.9%) and Boland decomposition (${sg(N.boland_alone)}%). Both are now included (Fig. 11; single effects given in the text). With every lower end the model reaches ${f1(N.stack["+ GHI -5 %"].pct)}% of baseline, i.e. the measurement (81%) is reached.`,
    `This changed the conclusion. The earlier sentence 'the remainder cannot be explained by the nine factors' was removed. New text: the budget reaches the measurement only at its joint extreme, which is implausible because (i) the isotropic model underestimates tilted irradiance on clear days [27], (ii) all lower ends together give ${sg(N.annual_all_lowest)}% annually, far below the 5th percentile (${sg(N.pct05[0])}%), and (iii) the same setting underestimates the clear day of 10 Feb by about ${Math.round((N.stack["+ GHI -5 %"].rfeb - 1) * 100)}%.`], "4.4; Fig. 8; Fig. 11"],
  ["7. High correlation but no accurate prediction; systematic overestimate of about 19% on clear days.",
   ["Agreed and stated directly: correlation shows only the shape; the level is wrong. The ratio is now defined explicitly as R = ΣP_actual / ΣP_model (Eq. 4). Table 3 now gives MBE, nMBE, RMSE, nRMSE and r for all five clear-sky records (nMBE +23% and +24%, nRMSE 27% and 31% in October).",
    `A leave-one-day-out test shows that a single correction factor does not transfer (factor from 17 Oct leaves ${sg(N.loo["2026-02-10"])}% on 10 Feb and ${sg(N.loo["2025-08-07"])}% on 7 Aug). The paper no longer claims predictive accuracy; it claims agreement in annual energy (counters) and a clear-day bias at hourly scale.`], "4.2 (Eq. 4); 4.3; Table 3; Fig. 9; 5; 6"],
];
const table = new Table({
  width: { size: W.reduce((a, b) => a + b), type: WidthType.DXA }, columnWidths: W,
  rows: rows.map((r, i) => new TableRow({ tableHeader: i === 0, cantSplit: true, children: r.map((c, j) => cell(c, W[j], { head: i === 0 })) })),
});
const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 21 } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    children: [
      P("Response to Review — CSME 2026 paper", { bold: true, size: 28 }),
      P("A pvlib-Based Computational Model of a Multi-Inverter Rooftop Photovoltaic Plant Driven by Public Weather Data: Sensitivity Analysis and Field Validation", { italics: true }),
      P("C. N. Govino, W.-R. Yang — revision of 30 October 2026 (6 pages)", { after: 160 }),
      P("Summary of changes", { bold: true, size: 23 }),
      P("The paper is now led by figures (12 figures, 3 tables, 6 pages). New: plant/measurement layout, three-phase waveforms, compact model chain, one-at-a-time chart with converged Sobol indices, inverter structure vs efficiency, and clear days vs 3.5-year counters (the 30 kW counter is faulty and shown as such); new tables: factor ranges with confidence intervals and error metrics. Two conclusions changed: the budget reaches the clear-day measurement only at an implausible joint extreme, and over 3.5 years the inverter counters agree with the model within 3%, so the clear-day shortfall is not a permanent plant loss.", { after: 160 }),
      table,
      P("", { after: 60 }),
      P("Code for every new number: src/rev_sobol_convergence.py, src/rev_analysis.py, src/rev_aliasing.py, src/rev_fig_*.py; collected in paper_rev/numbers.json.", { size: 19, italics: true }),
    ],
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(path.join(__dirname, "Response_to_review.docx"), b); console.log("written"); });
