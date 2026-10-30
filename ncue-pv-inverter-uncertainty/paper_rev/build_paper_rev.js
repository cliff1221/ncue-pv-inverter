// Revised CSME 2026 paper (after supervisor review). Build: node paper_rev/build_paper_rev.js
// Numbers that come from scripts are read from paper_rev/numbers.json (made by paper_rev/make_numbers.py).
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, AlignmentType, WidthType,
  BorderStyle, SectionType, Header, TabStopType, ShadingType, VerticalAlign,
} = require("docx");

const ROOT = path.join(__dirname, "..");
const N = JSON.parse(fs.readFileSync(path.join(__dirname, "numbers.json"), "utf8"));
const FONT = "Times New Roman";
const CJK = "MS PMincho";
const COLW = 4365;            // one column, DXA (approx. 7.70 cm)
const GAP = 340;              // column spacing, DXA
const FULLW = COLW * 2 + GAP; // 9070 DXA = 16.0 cm

// ---------------------------------------------------------------- inline markup
// {i}..{/i} italic, {b}..{/b} bold, {sub}..{/sub}, {sup}..{/sup}
function runs(s, base = {}) {
  const out = [];
  const st = { i: false, b: false, sub: false, sup: false };
  const re = /\{(\/?)(i|b|sub|sup)\}/g;
  let last = 0, m;
  const push = (t) => {
    if (!t) return;
    out.push(new TextRun({
      text: t, font: FONT, size: base.size || 20, italics: st.i || base.italics, bold: st.b || base.bold,
      subScript: st.sub, superScript: st.sup, color: base.color,
    }));
  };
  while ((m = re.exec(s)) !== null) {
    push(s.slice(last, m.index));
    st[m[2]] = m[1] !== "/";
    last = re.lastIndex;
  }
  push(s.slice(last));
  return out;
}
const body = (s, o = {}) => new Paragraph({
  children: runs(s, o), alignment: o.align || AlignmentType.JUSTIFIED,
  indent: o.noIndent ? undefined : { firstLine: 400 }, spacing: { after: o.after ?? 0, before: o.before ?? 0, line: 240 },
});
const sec = (s) => new Paragraph({ children: runs(s, { size: 22, bold: true }), alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 160, after: 80 } });
const sub = (s) => new Paragraph({ children: runs(s, { size: 20, bold: true }), keepNext: true, spacing: { before: 100, after: 40 } });
const caption = (s) => new Paragraph({ children: runs(s, { size: 18 }), alignment: AlignmentType.JUSTIFIED, spacing: { before: 40, after: 120 } });
const tcap = (s) => new Paragraph({ children: runs(s, { size: 18 }), alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 80, after: 40 } });
function img(file, wIn, o = {}) {
  const buf = fs.readFileSync(path.join(ROOT, file));
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const wpx = Math.round(wIn * 96);
  return new Paragraph({
    alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: o.before ?? 60, after: 0 },
    children: [new ImageRun({ type: "png", data: buf, transformation: { width: wpx, height: Math.round(wpx * h / w) },
      altText: { title: o.alt || file, description: o.alt || file, name: path.basename(file) } })],
  });
}
const eq = (s, num) => new Paragraph({
  tabStops: [{ type: TabStopType.CENTER, position: Math.round(COLW / 2) }, { type: TabStopType.RIGHT, position: COLW }],
  spacing: { before: 60, after: 60 },
  children: [new TextRun({ text: "\t", font: FONT, size: 20 }), ...runs(s), new TextRun({ text: "\t(" + num + ")", font: FONT, size: 20 })],
});

// ---------------------------------------------------------------- tables (three-line style)
const NONE = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const RULE = (sz) => ({ style: BorderStyle.SINGLE, size: sz, color: "000000" });
function table(rows, widths, o = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const nR = rows.length;
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths, alignment: AlignmentType.CENTER,
    borders: { top: NONE, bottom: NONE, left: NONE, right: NONE, insideHorizontal: NONE, insideVertical: NONE },
    rows: rows.map((r, ri) => new TableRow({
      cantSplit: true,
      children: r.map((c, ci) => new TableCell({
        width: { size: widths[ci], type: WidthType.DXA },
        margins: { top: 15, bottom: 15, left: 35, right: 35 }, verticalAlign: VerticalAlign.CENTER,
        borders: {
          top: ri === 0 ? RULE(8) : (ri === 1 ? RULE(4) : NONE), bottom: ri === nR - 1 ? RULE(8) : NONE,
          left: NONE, right: NONE,
        },
        children: [new Paragraph({
          keepNext: ri < nR - 1, keepLines: true,
          alignment: ci === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
          children: runs(String(c), { size: o.size || 16, bold: ri === 0 }),
        })],
      })),
    })),
  });
}
const f1 = (x) => Number(x).toFixed(1), f2 = (x) => Number(x).toFixed(2), f3 = (x) => Number(x).toFixed(3);
const sgn = (x, d = 1) => (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(d);

// ---------------------------------------------------------------- header
const header = new Header({
  children: [
    new Paragraph({ children: [
      new TextRun({ text: "中國機械工程學會第", font: CJK, size: 18 }), new TextRun({ text: " 43 ", font: FONT, size: 18 }),
      new TextRun({ text: "屆全國學術研討會", font: CJK, size: 18 }), new TextRun({ text: "(CSME2026)", font: FONT, size: 18 }),
      new TextRun({ text: "國立中正大學 嘉義縣", font: CJK, size: 18 })] }),
    new Paragraph({ children: [
      new TextRun({ text: "2026 ", font: FONT, size: 18 }), new TextRun({ text: "年", font: CJK, size: 18 }),
      new TextRun({ text: " 12 ", font: FONT, size: 18 }), new TextRun({ text: "月", font: CJK, size: 18 }),
      new TextRun({ text: " 4 ", font: FONT, size: 18 }), new TextRun({ text: "日、", font: CJK, size: 18 }),
      new TextRun({ text: "5 ", font: FONT, size: 18 }), new TextRun({ text: "日", font: CJK, size: 18 })] }),
  ],
});

// ================================================================ CONTENT
const S = N.sobol05, S10 = N.sobol10;
const st = (k, src = S) => `${f3(src[k].ST)} ± ${f3(src[k].ST_conf)}`;

// ---------- title block (one column)
const titleBlock = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 240, after: 120 }, children: runs(
    "A pvlib-Based Computational Model of a Multi-Inverter Rooftop Photovoltaic Plant Driven by Public Weather Data: Sensitivity Analysis and Field Validation",
    { size: 28, bold: true }) }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: runs("Cliff Nathanael Govino{sup}*{/sup}, Wen-Ren Yang", { size: 24 }) }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: runs("International Master Program of Engineering, National Changhua University of Education,", { size: 24 }) }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: runs("Changhua, Taiwan", { size: 24 }) }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: runs("{sup}*{/sup}Email: cliffgovin@gmail.com", { size: 20 }) }),
];

// ---------- abstract to section 2.1 (two columns)
const A = N.counters;
const part1 = [
  sec("Abstract"),
  body(`The energy output of a rooftop photovoltaic (PV) plant is often estimated from module datasheets and public weather data. We model a 139.5 kWp rooftop plant in Taiwan (372 modules; one 30 kW and two 50 kW inverters) with pvlib and rank nine uncertain factors in a Sobol analysis for the year 2023 (${N.sobol_runs.toLocaleString("en-US")} runs; the total indices change by less than ${f2(Math.max(0.01, N.conv_maxdiff05))} between 1,024 and 4,096 base samples). DC loss and irradiation error account for 84% of the variance and the inverter model for 7%. Separate runs show that the inverter effect comes from the assumed nominal efficiency (2.6% between 0.96 and 0.985) and hardly from the shape of the efficiency curve (0.4%). The model is compared with the AC power of the three inverters, recorded at the common output on 16 to 19 October 2026 and in seven two-hour records. On two clear autumn days the plant delivered 81% of the modeled energy (normalized mean bias error +23% and +24%), although the hourly profile is reproduced (r = 0.99 and 0.97). This gap is closed only when all factors are set to their lowest ends at the same time, and the same setting then underestimates a clear February day by 6%. Over 3.5 years, however, the energy counters of the two 50 kW inverters give ${Math.round(A.left.y_cnt)} and ${Math.round(A.middle.y_cnt)} kWh/kWp per year, 1% and 3% above the model. The model thus agrees with the long-term energy but is biased on clear days at hourly scale, and the cause cannot be identified without irradiance measured on site.`),
  new Paragraph({ spacing: { before: 60, after: 0 }, children: [...runs("{b}Keywords:{/b} Photovoltaic; Inverter modeling; pvlib; Uncertainty budget; Field validation")] }),
  sec("1. Introduction"),
  body("When no verified power measurements are available, the energy output of a rooftop PV system can be estimated from the technical specifications of its modules and from public weather data. The pvlib Python library provides the main building blocks for such modeling [1], [2], but the results depend on the assumptions made at each step. One of them concerns the inverter. A constant efficiency with clipping is the simplest baseline, while PVWatts [3] accounts for the variation of efficiency with load. The Sandia [4] and ADR [5] models need inverter performance data that manufacturer datasheets do not always give. Data resolution is a further issue: hourly weather data average out short periods of high irradiance, so the model underestimates inverter clipping [6]."),
  body("Earlier work has examined the sources of uncertainty in PV energy modeling. A Sandia study found that the plane-of-array and effective irradiance models were the main contributors [7]. IEA PVPS Task 13 reports annual uncertainties of 2 to 6% for satellite-derived irradiation [8], and a blind intercomparison attributed the remaining errors to modeling skill, human error and derate assumptions [9]. These studies do not fully address a single rooftop plant, where the weather data may come from a distant source and the real losses of the system are not represented in module datasheets."),
  body("This study examines the 139.5 kWp rooftop plant of National Changhua University of Education (NCUE), Taiwan, and asks three questions: how large the effect of the inverter model is compared with other uncertain factors over a year, and whether it comes from the model structure or from the assumed efficiency; how much it matters whether the weather data come from a station 21 km away or from ERA5 [10]; and whether the resulting uncertainty budget encloses the energy the plant actually delivers. The first two are answered with 2023 weather data and a variance-based sensitivity analysis [11], [12]. The third is answered with AC power measured in 2025 and 2026 and with the lifetime energy counters of the inverters."),
  sec("2. Plant, Data and Model"),
  sub("2.1 Plant"),
  body("The plant is located at 24.066°N, 120.559°E on the roof of the College of Engineering building. It consists of 372 AJP-S672-375 modules [13] (139.5 kWp) on open steel racks, all facing south at a tilt of 23°, and feeds one 30 kW and two 50 kW inverters [14] (Fig. 1, Table 1). All electricity is fed into the grid and there is no battery storage."),
  body("The design drawings specify 144, 144 and 84 modules in strings of 16 or 18. A site inspection in October 2026, based on the hand annotations of the drawings, the module count of each roof block and the string currents and MPPT voltages on the inverter displays, found a different layout (Fig. 1): the left 50 kW inverter has nine strings (145 modules), the middle one seven strings of 20 (140) and the 30 kW inverter five strings, including a 21-module string and a 16- and an 18-module string in parallel on one MPPT (87). The total, 372 modules in 21 strings, is unchanged, and switching from the design to this layout changes the annual energy by only +0.02%. Two blocks of the left inverter sit on a tower about 7 m high, next to an empty steel frame of the same height that the drawings mark as a source of shading. The event log of the middle inverter shows a fan fault with power de-rating, and the lifetime counter of the 30 kW inverter is faulty (Section 4.5)."),
];

// ---------- Fig. 1 full width
const fig1 = [
  img("paper_figs_rev/fig1_layout.png", 6.3, { alt: "Plant layout: roof blocks, strings, inverters and Hioki measurement point" }),
  caption("Fig. 1 Plant layout. (a) Roof blocks and their assignment to the inverters (positions schematic). (b) Strings per MPPT, AC connection and the measurement point of the recorder at the common AC output of the three inverters."),
];

// ---------- rest (two columns)
const T1 = table([
  ["Item", "Value"],
  ["Module", "375 W, γ = −0.44 %/°C, NOCT 46 ± 2 °C"],
  ["Inverter 30 / 50 kW", "η{sub}max{/sub} 98.6 / 98.5%, MPPT 420–800 / 480–820 V"],
  ["Modules (left / middle / right)", "145 / 140 / 87"],
  ["Capacity (kWp)", "54.4 / 52.5 / 32.6"],
  ["DC/AC ratio", "1.09 / 1.05 / 1.09"],
  ["String length (modules)", "16–17 / 20 / 16–21"],
], [1700, 2665]);

const AL = N.aliasing;
const part2 = [
  tcap("Table 1 Plant data (as built)."), T1,
  sub("2.2 Weather data"),
  body("The weather data are hourly irradiation and temperature from the CWA Tianzhong station (467270) [15], 21.4 km from the site, and hourly ERA5 data obtained through PVGIS [16], [17]. The hour label refers to the end of the hour (1 MJ/m² per hour equals 277.8 W/m²), and one missing hour was interpolated. The annual irradiation is 1626 kWh/m². No pyranometer is installed on the roof, so the irradiance on the modules is not measured."),
  sub("2.3 Power measurement"),
  body("The AC power at the common output of the three inverters was recorded with a Hioki MR8875 [18] (Fig. 1b, Fig. 2a). Three clamp sensors measure the line currents {i}i{/i}{sub}a{/sub}, {i}i{/i}{sub}b{/sub} and {i}i{/i}{sub}c{/sub}, and three voltage channels measure the line-to-line voltages {i}v{/i}{sub}ab{/sub}, {i}v{/i}{sub}bc{/sub} and {i}v{/i}{sub}ca{/sub}. The system has three wires and no neutral, so {i}i{/i}{sub}a{/sub} + {i}i{/i}{sub}b{/sub} + {i}i{/i}{sub}c{/sub} = 0 and the active power follows from two products (two-wattmeter or Aron method, valid for unbalanced and distorted waveforms [28]):"),
  eq("{i}P{/i} = ⟨{i}v{/i}{sub}ab{/sub} {i}i{/i}{sub}a{/sub} − {i}v{/i}{sub}bc{/sub} {i}i{/i}{sub}c{/sub}⟩", 1),
  body("The three cyclic forms of Eq. (1) agree within 1%. Fig. 2b shows why line-to-line voltages must not be multiplied with the current of the same channel: {i}V{/i}{sub}ab{/sub} leads {i}I{/i}{sub}a{/sub} by 30° + φ, so the sum of the three products gives 3{i}V{/i}{sub}LL{/sub}{i}I{/i} cos 30°, about 1.5 times the true power."),
  img("paper_figs_rev/fig2_3phase.png", 3.2, { alt: "Three-wire connection of the recorder and phasor diagram" }),
  caption("Fig. 2 (a) Connection of the recorder to the three-wire AC bus. (b) Phasor diagram with the line-to-line voltages, the phase currents and the displacement angle φ (exaggerated)."),
  body(`The phasors computed from the records confirm the setting of Fig. 2b. The three line-to-line voltages are 120° apart within ±1.5° (sequence a-b-c), the currents lag the phase voltages by 0.5° to 4.3°, and the voltage and current unbalance average 0.9% (maxima 3.8% and 3.6%). The mean line-to-line voltage is 383 V, within the inverter limits of 334 to 418 V. The power computed from the fundamental phasors agrees with Eq. (1) with a median difference of −0.13%, and the daytime power factor is 0.995.`),
  body(`The main record runs from 19:46 on 16 October 2026 to 18:05 on 19 October 2026. It was sampled at 2 ms, thinned to every fifth sample (10 ms) and averaged to one-minute values (4,201 values, no gap longer than 90 s). Seven records of about two hours were taken in 2025 and 2026 at 0.2 ms and thinned to 20 ms. Thinning without filtering aliases the 60 Hz waveforms, but the mean power is still correct when the sampling instants are spread evenly over the cycle: at 10 ms and 20 ms the samples fall on five equally spaced phase positions, and the power ripple at twice the grid frequency and at the harmonic frequencies averages out over a minute. A thinning interval that is a whole number of cycles, such as 200 ms, places all samples at the same phase and was therefore avoided. Because the raw 2 ms files are not kept, this was tested with ${AL.ncases} synthetic minutes built from the measured properties above (unbalance up to 3.8%, displacement up to 5°, current harmonics of 3% (5th) to 1% (13th), power change of up to ±30% within the minute). With the grid frequency between 59.95 and 60.05 Hz, the one-minute power from 10 ms and 20 ms samples differs from a 0.1 ms reference by at most ${f2(AL.max10_free)}% and ${f2(AL.max20_free)}%, and by at most ${f2(AL.max10_locked)}% and ${f2(AL.max20_locked)}% with the frequency locked at exactly 60 Hz. Samples 200 ms apart err by up to ${f1(AL.max200_free)}% and ${f0b(AL.max200_locked)}% in the same two cases. The thinning therefore does not bias the active power.`),
  body(`The measurement chain was not calibrated. Two checks are available. The night-time offset is −0.011 kW. On 18 October the "today" energy shown by the three inverter displays summed to 572 kWh at 16:58, ${f1((N.display_over_hioki - 1) * 100)}% more than the 555 kWh integrated by the recorder up to that time; the middle inverter showed 39.3% of the recorded energy, against a module share of 37.6%.`),
  sub("2.4 Model chain"),
  body("GHI is split with the Erbs model [19], transposed to the tilted plane with the Perez model [20] (albedo 0.25), and cell temperature follows Ross [21] with NOCT 46 °C (Fig. 3). DC power is calculated with PVWatts [3],"),
  eq("{i}P{/i}{sub}dc{/sub} = {i}P{/i}{sub}0{/sub}({i}G{/i}/1000)[1 + γ({i}T{/i}{sub}c{/sub} − 25)](1 − {i}f{/i}{sub}dc{/sub})", 2),
  body("with {i}f{/i}{sub}dc{/sub} = 8.7% (11.4% including the default shading loss). Each inverter is modeled separately in three ways: constant efficiency with clipping, PVWatts-DS (datasheet peak efficiency used as nominal efficiency, an upper bound) and PVWatts-G (nominal efficiency 0.96, the pvlib default). Our implementation equals pvlib.inverter.pvwatts to within 0 W. The baseline has no incidence-angle modifier; one variant adds the Martin and Ruiz model [22] with the generic coefficient {i}a{/i}{sub}r{/sub} = 0.16. The performance ratio follows IEC 61724-1 [23]."),
  img("paper_figs/fig_flow.png", 2.9, { alt: "Model chain and pvlib functions" }),
  caption("Fig. 3 The model chain and the pvlib functions used. Orange: inverter stage implemented and checked here."),
];

// ---------- Section 3
const T2 = table([
  ["Factor", "Range, distribution and basis", "OAT (%)", "{i}S{/i}{sub}T{/sub} ±5%", "{i}S{/i}{sub}T{/sub} ±10%"],
  ["DC loss", "0–11.4%, uniform; PVWatts total loss without / with shading [3]", "−3.0 / +9.6", st("rugi_DC"), st("rugi_DC", S10)],
  ["GHI error", "±5% (±10%), uniform; pyranometer class and distance [8]", "−5.1 / +5.0", st("galat_GHI"), st("galat_GHI", S10)],
  ["Inverter model", "3 formulations, equal weight", "−2.6 / +0.4", st("model_inverter"), st("model_inverter", S10)],
  ["Transposition", "5 pvlib models, equal weight", "−2.5 / +1.0", st("transposisi"), st("transposisi", S10)],
  ["Cell temperature", "Ross, Faiman, SAPM, equal weight", "0.0 / +2.0", st("model_suhu_sel"), st("model_suhu_sel", S10)],
  ["Decomposition", "4 pvlib models, equal weight", "−0.7 / +0.2", st("dekomposisi_GHI"), st("dekomposisi_GHI", S10)],
  ["NOCT", "44–48 °C, uniform; datasheet 46 ± 2 °C", "−0.8 / +0.8", st("NOCT"), st("NOCT", S10)],
  ["Time shift", "−0.5, 0, +0.5 h; meaning of hour label", "−0.1 / 0.0", st("geser_waktu"), st("geser_waktu", S10)],
  ["Mapping", "2 layouts that satisfy the inverter limits", "0.0 / 0.0", st("pemetaan"), st("pemetaan", S10)],
], [1500, 4370, 1000, 1100, 1100], { size: 16 });

const AS = N.structure;
const T3 = table([
  ["Inverter setting (as-built layout, 2023)", "Δ{i}E{/i} (%)"],
  ["PVWatts, η{sub}nom{/sub} = datasheet peak (PVWatts-DS, reference)", "0.00"],
  ["Same η = 0.985: constant / PVWatts", `${sgn(AS["constant eta = 0.985"], 2)} / ${sgn(AS["PVWatts eta_nom = 0.985"], 2)}`],
  ["Same η = 0.96: constant / PVWatts", `${sgn(AS["constant eta = 0.96"], 2)} / ${sgn(AS["PVWatts eta_nom = 0.96"], 2)}`],
  ["Same peak efficiency: constant / PVWatts", `${sgn(AS["constant eta = datasheet peak"], 2)} / ${sgn(AS["PVWatts, peak of curve = datasheet peak"], 2)}`],
  ["PVWatts, η{sub}nom{/sub} = 0.96 / 0.97 / 0.98", `${sgn(AS["PVWatts eta_nom = 0.96"], 2)} / ${sgn(AS["PVWatts eta_nom = 0.97"], 2)} / ${sgn(AS["PVWatts eta_nom = 0.98"], 2)}`],
], [3300, 1065]);

const part3 = [
  sec("3. Annual Uncertainty Budget"),
  sub("3.1 Factors and ranges"),
  body("Nine factors were varied (Table 2). Continuous factors are uniformly distributed over the stated range and model choices are drawn with equal weight among the options available in pvlib. The DC-loss range runs from no loss to the PVWatts default total loss including shading [3]; the GHI error of ±5% reflects the uncertainty of station pyranometers and of irradiation at a distant site [8], and ±10% is reported as a wider case. These ranges are assumptions, and the ranking of the factors depends on them: a wider GHI range moves weight from DC loss to irradiation (Table 2). Saltelli sampling [12] with SALib [26] was used for the first-order and total indices."),
  sub("3.2 Results and convergence"),
  body(`The baseline gives 195 MWh AC (1399 kWh/kWp). The 5th to 95th percentile of the annual energy spans ${sgn(N.pct05[0])}% to ${sgn(N.pct05[2])}% of the baseline. DC loss and irradiation error together explain 84% of the variance (Fig. 4, Table 2); the inverter model ranks third (7%, and 3% with ±10% GHI error). Interactions are negligible (the sums of the first-order and total indices differ by ${f3(N.interaction05)}), and the mapping changes the energy by less than 0.01%. At the baseline loss no inverter reaches its limit in the hourly data; without DC loss, clipping amounts to at most 21 kWh per year.`),
  body(`To test convergence, the number of base samples was raised from 64 to 4,096 (${N.sobol_runs.toLocaleString("en-US")} model runs), and five further scrambling seeds were run at 1,024. Between 1,024 and 4,096 samples the total indices change by at most ${f3(N.conv_maxdiff05)} (±5% case) and ${f3(N.conv_maxdiff10)} (±10%), the standard deviation over the seeds is at most ${f3(N.seed_sd05)}, and the ranking of the first five factors does not change from ${N.rank_stable_from} samples onward. Table 2 gives the total indices at 4,096 samples with 95% bootstrap confidence intervals. The intervals of the first five factors do not overlap, so their order is resolved; the last four factors have indices below 0.005 and are not ranked.`),
  img("paper_figs/fig_sens.png", 3.15, { alt: "One-at-a-time change and Sobol total index" }),
  caption("Fig. 4 Change in annual AC energy when one factor is moved within its range: orange = setting that lowers the energy most, blue = setting that raises it most; text: Sobol total index (1,024 samples)."),
];
const table2 = [
  tcap("Table 2 Factors, ranges, one-at-a-time (OAT) change and Sobol total index {i}S{/i}{sub}T{/sub} (4,096 base samples, 95% confidence interval)."),
  T2, new Paragraph({ spacing: { after: 80 }, children: [] }),
];
const part3b = [
  sub("3.3 Inverter: model structure or efficiency"),
  body("The three inverter formulations differ in two ways at once: in the shape of the efficiency curve and in the nominal efficiency assumed. To separate the two, each structure was run with the same efficiency and one structure was run with different efficiencies (Table 3). With the same value of η, a constant efficiency gives 0.36 to 0.37% more energy than PVWatts, because PVWatts lowers the efficiency at part load. When both are given the same peak efficiency (the PVWatts curve peaks 0.26% above its nominal value), the difference is 0.6%. Lowering the nominal efficiency from 0.985 to 0.96 within PVWatts removes 2.6%. The −2.6% of PVWatts-G in the budget is therefore an efficiency assumption, not a property of the model structure. On the two clear October days, where most energy is produced near full load, the two structures with the same η differ by less than 0.1%."),
  tcap("Table 3 Model structure against assumed efficiency."), T3,
  sub("3.4 Weather source"),
  body("Station and ERA5 irradiation differ by a mean bias of +2.6% and an RMSE of 37% (r = 0.83) over the daytime hours of 2023. The annual modeled energy changes by +3.4% when ERA5 replaces the station, but the monthly energy changes by −12% to +19%, because biases of opposite sign cancel over the year (Fig. 5). For monthly estimates the weather source is therefore a larger uncertainty than the inverter formulation."),
  img("paper_figs/fig_hourly.png", 3.15, { alt: "Monthly AC energy, station vs ERA5" }),
  caption("Fig. 5 Monthly AC energy of the same model chain driven by station GHI or ERA5 GHI (2023)."),
];

// ---------- Section 4
const M = N.metrics;
const mrow = (d, lab) => { const r = M[d]; return [lab, `${r.hours}`, f2(r.ratio), sgn(r.MBE_kW), sgn(r.nMBE_pct, 0), f1(r.RMSE_kW), f1(r.nRMSE_pct), (r.r === null || r.hours < 5) ? "–" : f2(r.r)]; };
const T4 = table([
  ["Record", "h", "Meas./ model", "MBE (kW)", "nMBE (%)", "RMSE (kW)", "nRMSE (%)", "{i}r{/i}"],
  mrow("2026-10-17", "17 Oct 26"), mrow("2026-10-18", "18 Oct 26"), mrow("2026-02-10", "10 Feb 26"),
  mrow("2025-12-21", "21 Dec 25"), mrow("2025-08-07", "7 Aug 25"),
], [830, 230, 560, 560, 530, 560, 580, 515], { size: 15 });

const B = N.stack;
const T5 = table([
  ["Change", "Δ energy (%)", "Meas./model"],
  ["Baseline", "0.0", "0.81"],
  ["Constant efficiency", "0.0", "0.81"],
  ["PVWatts-G", "−2.6", "0.83"],
  ["DC loss 0% / 11.4%", "+9.5 / −3.0", "0.74 / 0.83"],
  ["GHI −5% / +5%", "−4.3 / +4.3", "0.85 / 0.78"],
  ["NOCT 48 / 44 °C", "−1.0 / +1.0", "0.82 / 0.80"],
  ["Incidence-angle loss", "−1.8", "0.82"],
  ["Isotropic transposition", "−3.9", "0.84"],
  ["Boland decomposition", sgn(N.boland_alone), f2(N.boland_ratio)],
], [2000, 1250, 1115]);

const L = N.loo;
const part4 = [
  sec("4. Field Validation"),
  sub("4.1 Measured output"),
  body("Fig. 6 shows the three recorded days. On 17 and 18 October the plant produced 585 and 557 kWh (4.20 and 3.99 kWh/kWp). The maximum one-minute power is 100.5 kW (77% of the 130 kW rating), so there is no sign of clipping. According to the station, both days were almost free of cloud (97 and 94% of clear-sky irradiation), yet the power curve is not smooth: between 10:00 and 14:00 the standard deviation of the one-minute power changes is 0.06 and 0.13 of the mean power, compared with 0.003 on a clear day in February. The AC data alone cannot show whether these dips are caused by small clouds, aerosol or inverter behavior."),
  img("paper_figs/fig_meas3d.png", 3.0, { alt: "Measured AC power 16-19 Oct 2026" }),
  caption("Fig. 6 Measured AC power, 16 to 19 October 2026 (one-minute means)."),
  sub("4.2 Model against measurement"),
  body(`Fig. 7 and Table 4 compare the hourly means with the baseline. A high correlation shows only that the shape of the curve is reproduced (r = 0.99 and 0.97; centroid shift of 0.05 and 0.10 h); the error of the level is given by the mean bias error (MBE) and the root mean square error (RMSE), normalized by the mean measured power. The model is higher in almost every hour, by 12.3 kW on average (nMBE +23% and +24%, nRMSE 27% and 31%). The measured energy is 0.81 of the modeled energy on both days, and the measured performance ratio is 0.63 against 0.78 for the model. A third clear day, 19 October (to 18:00), gives the same ratio (0.80). The ratio shows no consistent morning/afternoon asymmetry (0.82 and 0.80 on 17 October, 0.76 and 0.86 on 18 October; Fig. 8), so a fixed one-sided obstruction is unlikely to be the main cause. With this bias the model does not predict the hourly power on clear days.`),
  img("paper_figs_rev/fig_modelvs_rev.png", 3.15, { alt: "Hourly measured and modeled power, 17-18 Oct" }),
  caption("Fig. 7 Hourly mean AC power, measured and modeled. The band runs from the baseline to the stacked lower bounds of Section 4.4 (all factors at their lowest end)."),
  tcap("Table 4 Error metrics on the clear-sky records (hours with at least 20 recorded minutes, weighted by minutes; model baseline; {i}r{/i} only for full days)."), T4,
  img("paper_figs/fig_ratio_hour.png", 3.0, { alt: "Measured over modeled by hour" }),
  caption("Fig. 8 Measured over modeled hourly power by hour for the clear-sky records."),
  sub("4.3 Other records"),
  body(`Across the nine days with station data the ratio of measured to modeled energy lies between 0.65 and 1.01 (Fig. 9). On the five days with a clear-sky fraction above 0.9 it ranges from 0.80 to 1.01 (Table 4). Cloudy and rainy days carry little weight because a station 21 km away does not follow the cloud above the roof. With so few records a seasonal pattern cannot be separated from day-to-day differences. A single correction factor does not transfer between days either: the factor fitted on 17 October (${f3(L.k)}) leaves a bias of ${sgn(L["2026-10-18"])}% on 18 October and ${sgn(L["2025-12-21"])}% on 21 December, but ${sgn(L["2026-02-10"])}% on 10 February and ${sgn(L["2025-08-07"])}% on 7 August. The ratio must therefore not be used as an annual correction.`),
  img("paper_figs/fig_campaigns.png", 3.0, { alt: "Clear-sky fraction and ratio per record" }),
  caption("Fig. 9 (a) Clear-sky fraction of the station irradiation and (b) measured over modeled energy per record. Blue: fraction above 0.9."),
  sub("4.4 Closing the budget"),
  body(`Table 5 lists single changes, and Fig. 10 stacks the lower end of every factor on the baseline of 17 and 18 October. The earlier version of this stack left out two model options that lower the energy: isotropic transposition (−3.9% alone) and the Boland decomposition (${sgn(N.boland_alone)}%). They are now included. With the PVWatts-G inverter, a DC loss of 11.4%, NOCT 48 °C, the incidence-angle loss, isotropic transposition and Boland decomposition, the model falls to ${f1(B["+ Boland decomposition"].pct)}%, and an irradiation 5% lower brings it to ${f1(B["+ GHI -5 %"].pct)}%, close to the measured 81% (ratio ${f2(B["+ GHI -5 %"].r17)} and ${f2(B["+ GHI -5 %"].r18)}).`),
  body(`The budget can thus reach the measurement, but only at its joint extreme, which is not a plausible state for three reasons. First, the isotropic model ignores circumsolar and horizon brightening and underestimates the irradiance on tilted planes under clear skies [27]; on days that were 94 to 97% of clear-sky irradiation it is the least suitable option. Second, all lower ends together lower the annual energy by ${f1(-N.annual_all_lowest)}%, far beyond the 5th percentile of the budget (${sgn(N.pct05[0])}%), which the sampled distribution almost never reaches. Third, the same setting on 10 February gives a ratio of ${f2(B["+ GHI -5 %"].rfeb)}, i.e. it underestimates that clear day by ${f0(B["+ GHI -5 %"].rfeb)}%. No single set of factor values fits the clear days in October and February.`),
  tcap("Table 5 Effect of single changes on the modeled energy of 17 and 18 October (mean of both days)."), T5,
  img("paper_figs_rev/fig_closure_rev.png", 3.0, { alt: "Stacked lower bounds" }),
  caption("Fig. 10 Modeled energy as a percentage of the baseline with the lower ends stacked; orange: options added in this revision; red line: measured."),
  sub("4.5 Long-term check with the inverter energy counters"),
  body(`The short records cover only a few days. A longer check is given by the lifetime energy counters of the inverters, read on 18 October 2026, 1280 days after commissioning on 17 April 2023: ${A.left.kwh.toLocaleString("en-US")} kWh for the left and ${A.middle.kwh.toLocaleString("en-US")} kWh for the middle 50 kW inverter. The model with the as-built layout and 2023 weather, repeated for each calendar day of the same period, gives ${f1(A.left.model / 1000)} and ${f1(A.middle.model / 1000)} MWh. The counters are thus ${f1((A.left.ratio - 1) * 100)}% and ${f1((A.middle.ratio - 1) * 100)}% above the model (${Math.round(A.left.y_cnt)} and ${Math.round(A.middle.y_cnt)} against 1399 kWh/kWp per year). The counter of the 30 kW inverter shows 3.6 GWh after 497,827 h, which is impossible, and was not used.`),
  body("This comparison has its own uncertainty: the counters are the inverters' own meters, which read 3% above the recorder on 18 October; the weather of 2024 to 2026 differs from 2023; module degradation is not modeled; and outages are included in the counters. Even so, a constant shortfall of 19% would have shown in 3.5 years of data. The clear-day bias is therefore not a permanent loss of the plant. Either the model is lower than the plant under other conditions, or the October days are atypical, or both. The short records, mostly from autumn and winter, do not show where the difference is made up; the only summer record (7 August 2025) gives 1.01."),
  sub("4.6 Causes and the inverter model"),
  body("The data narrow the cause but do not settle it. A large bias of the station irradiation on cloud-free days is unlikely, and a fixed one-sided shadow is not supported. Candidates on the plant side are shading by the tower and frame, soiling before the rainy season, string mismatch, the 21-module string on the 30 kW inverter, de-rating of the middle inverter, and short outages; on the measurement side, an uncalibrated recorder that reads about 3% below the inverter displays. Separating them requires irradiance in the plane of the array, inverter-level AC logging and string currents. The inverter formulations move the modeled energy by at most 2.6%, about a seventh of the gap, and all give the same correlation; AC data alone therefore cannot say which is better."),
];

// ---------- Section 5, 6, refs
const part5 = [
  sec("5. Discussion and Limitations"),
  body(`The nine-factor budget gives a 5th to 95th percentile range of ${sgn(N.pct05[0])}% to ${sgn(N.pct05[2])}% relative to the baseline. This range does not include the 19% shortfall measured on clear autumn days, and the budget reaches the measurement only at its joint extreme (Section 4.4). Over 3.5 years, on the other hand, the inverter counters agree with the model within 3%. The model is therefore suitable for an estimate of the annual energy at this site, with the uncertainty given by the budget, but not for hourly or daily prediction on clear days, where it overestimates the power by about 20%. An additional loss factor fitted to the clear days (0 to 20%) would raise the share of plant losses in the variance to about 62% and lower the share of the inverter formulation from 7% to 3%, but the counters do not support such a loss at annual scale, so it is not added to the budget.`),
  body("Several limitations apply. (1) The validation data cover three days and seven two-hour records, mostly from autumn and winter; the long-term check rests on two uncalibrated inverter counters and on 2023 weather. Monthly energy data of the utility meter and a year of logging would allow a seasonal comparison. (2) The irradiance comes from a station 21 km away, and no pyranometer or reference cell is installed on the roof, so the model error cannot be split into an irradiance part and a plant part; this is the most important gap. (3) The measurement chain was not calibrated, and only the combined AC output was recorded. (4) The sensitivity ranking depends on the ranges and distributions assigned to the factors (Table 2), and the stacked lower bounds are not independent of each other. (5) The cause of the clear-day shortfall has not been confirmed."),
  sec("6. Conclusions"),
  body("The datasheet-based model estimates an annual AC yield of 195 MWh (1399 kWh/kWp) for the 139.5 kWp plant. Changing the inverter model shifts this estimate by −2.6% to +0.4%, the third-largest source of uncertainty after DC loss and irradiation error, and this effect comes from the assumed efficiency rather than from the model structure (0.4 to 0.6%). The Sobol indices are converged at 4,096 samples, but their ranking depends on the assumed ranges. The choice of weather data matters more at monthly scale (−12% to +19%). On clear autumn days the plant produced 81% of the modeled energy (nMBE about +24%) although the daily profile is reproduced, and this gap is closed only when all lower bounds coincide. Over 3.5 years the inverter counters agree with the model within 3%. For this plant the model can be used for annual energy, but hourly prediction requires irradiance measured on the roof, which is the first step before the inverter model is refined further."),
  sec("Data Availability"),
  body("Code and data: https://github.com/cliff1221/ncue-pv-inverter.", { noIndent: true }),
  sec("References"),
];
const REFS = [
  "W. F. Holmgren, C. W. Hansen and M. A. Mikofski, “pvlib python: a python package for modeling solar energy systems,” Journal of Open Source Software, Vol. 3, No. 29, Article 884, 2018.",
  "K. S. Anderson, C. W. Hansen, W. F. Holmgren, M. A. Mikofski, A. R. Jensen and A. Driesse, “pvlib python: 2023 project update,” Journal of Open Source Software, Vol. 8, No. 92, Article 5994, 2023.",
  "A. P. Dobos, PVWatts Version 5 Manual, NREL/TP-6A20-62641, National Renewable Energy Laboratory, Golden, CO (2014).",
  "D. L. King, S. Gonzalez, G. M. Galbraith and W. E. Boyson, Performance Model for Grid-Connected Photovoltaic Inverters, SAND2007-5036, Sandia National Laboratories, Albuquerque, NM (2007).",
  "A. Driesse, P. Jain and S. Harrison, “Beyond the curves: Modeling the electrical efficiency of photovoltaic inverters,” Proceedings of the 33rd IEEE Photovoltaic Specialists Conference, San Diego, CA, USA (2008).",
  "B. Burger and R. Rüther, “Inverter sizing of grid-connected photovoltaic systems in the light of local solar resource distribution characteristics and temperature,” Solar Energy, Vol. 80, No. 1, pp. 32-45, 2006.",
  "Sandia National Laboratories, Uncertainty and Sensitivity Analysis for Photovoltaic System Modeling, SAND2013-10358, Albuquerque, NM (2013).",
  "C. Reise et al., Uncertainties in PV System Yield Predictions and Assessments, IEA PVPS Task 13, Report IEA-PVPS T13-12:2018 (2018).",
  "M. Theristis et al., “Blind photovoltaic modeling intercomparison: A multidimensional data analysis and lessons learned,” Progress in Photovoltaics: Research and Applications, Vol. 31, No. 11, pp. 1144-1157, 2023.",
  "H. Hersbach et al., “The ERA5 global reanalysis,” Quarterly Journal of the Royal Meteorological Society, Vol. 146, No. 730, pp. 1999-2049, 2020.",
  "I. M. Sobol’, “Global sensitivity indices for nonlinear mathematical models and their Monte Carlo estimates,” Mathematics and Computers in Simulation, Vol. 55, No. 1-3, pp. 271-280, 2001.",
  "A. Saltelli, P. Annoni, I. Azzini, F. Campolongo, M. Ratto and S. Tarantola, “Variance based sensitivity analysis of model output. Design and estimator for the total sensitivity index,” Computer Physics Communications, Vol. 181, No. 2, pp. 259-270, 2010.",
  "AJP-S672-365W~375W Datasheet, Anji Technology.",
  "CyberPower, CPSPV22000-36000ETLA-WB and CPSPV50000-66000ETL-WB Datasheets, Cyber Power Systems, Inc. (2024-2025).",
  "Central Weather Administration, CWA Observation Data Inquiry System (CODiS), https://codis.cwa.gov.tw/",
  "European Commission Joint Research Centre, Photovoltaic Geographical Information System (PVGIS) v5.3, https://re.jrc.ec.europa.eu/pvg_tools/",
  "T. Huld, R. Müller and A. Gambardella, “A new solar radiation database for estimating PV performance in Europe and Africa,” Solar Energy, Vol. 86, No. 6, pp. 1803-1815, 2012.",
  "Hioki E.E. Corporation, MR8875 Memory HiCorder Instruction Manual, Nagano, Japan.",
  "D. G. Erbs, S. A. Klein and J. A. Duffie, “Estimation of the diffuse radiation fraction for hourly, daily and monthly-average global radiation,” Solar Energy, Vol. 28, No. 4, pp. 293-302, 1982.",
  "R. Perez, P. Ineichen, R. Seals, J. Michalsky and R. Stewart, “Modeling daylight availability and irradiance components from direct and global irradiance,” Solar Energy, Vol. 44, No. 5, pp. 271-289, 1990.",
  "R. G. Ross Jr., “Design techniques for flat-plate photovoltaic arrays,” Proceedings of the 15th IEEE Photovoltaic Specialists Conference, Orlando, FL, USA (1981).",
  "N. Martin and J. M. Ruiz, “Calculation of the PV modules angular losses under field conditions by means of an analytical model,” Solar Energy Materials and Solar Cells, Vol. 70, No. 1, pp. 25-38, 2001.",
  "IEC 61724-1:2021, Photovoltaic system performance - Part 1: Monitoring, International Electrotechnical Commission, Geneva (2021).",
  "D. Faiman, “Assessing the outdoor operating temperature of photovoltaic modules,” Progress in Photovoltaics: Research and Applications, Vol. 16, No. 4, pp. 307-315, 2008.",
  "D. L. King, W. E. Boyson and J. A. Kratochvil, Photovoltaic Array Performance Model, SAND2004-3535, Sandia National Laboratories, Albuquerque, NM (2004).",
  "J. Herman and W. Usher, “SALib: An open-source Python library for sensitivity analysis,” Journal of Open Source Software, Vol. 2, No. 9, Article 97, 2017.",
  "P. G. Loutzenhiser, H. Manz, C. Felsmann, P. A. Strachan, T. Frank and G. M. Maxwell, “Empirical validation of models to compute solar irradiance on inclined surfaces for building energy simulation,” Solar Energy, Vol. 81, No. 2, pp. 254-267, 2007.",
  "IEEE Std 1459-2010, IEEE Standard Definitions for the Measurement of Electric Power Quantities Under Sinusoidal, Nonsinusoidal, Balanced, or Unbalanced Conditions, IEEE, New York (2010).",
];
const refParas = REFS.map((r, i) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED, spacing: { after: 0 }, indent: { left: 340, hanging: 340 },
  children: runs(`${i + 1}. ${r}`, { size: 16 }),
}));
function f0(x) { return Math.abs((x - 1) * 100).toFixed(0); }
function f0b(x) { return Number(x).toFixed(0); }

// ================================================================ assemble
const page = { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1250, left: 1134, right: 1134, header: 600 } };
const two = { count: 2, space: GAP, equalWidth: true };
const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 20 } } } },
  sections: [
    { properties: { page }, headers: { default: header }, children: titleBlock },
    { properties: { page, type: SectionType.CONTINUOUS, column: two }, headers: { default: header }, children: part1 },
    { properties: { page, type: SectionType.CONTINUOUS }, headers: { default: header }, children: fig1 },
    { properties: { page, type: SectionType.CONTINUOUS, column: two }, headers: { default: header },
      children: [...part2, ...part3] },
    { properties: { page, type: SectionType.CONTINUOUS }, headers: { default: header }, children: table2 },
    { properties: { page, type: SectionType.CONTINUOUS, column: two }, headers: { default: header },
      children: [...part3b, ...part4, ...part5, ...refParas] },
  ],
});
Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(path.join(__dirname, "CSME2026_Govino_revised.docx"), b);
  console.log("written");
});
