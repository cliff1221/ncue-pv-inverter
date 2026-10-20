# A pvlib-Based Computational Model of a Multi-Inverter Rooftop Photovoltaic Plant Driven by Public Weather Data: Sensitivity Analysis and Field Validation.

Code and processed data for the CSME 2026 paper
"From Datasheet to Field: An Uncertainty Budget and One-Minute AC Validation of a 139.5 kWp Three-Inverter Rooftop PV Plant"
(C. N. Govino, W.-R. Yang, National Changhua University of Education, Taiwan).
[[Add DOI / citation after the Zenodo release]]

The repository has two parts:
1. **Annual uncertainty budget (2023 weather)**: pvlib model chain, one-at-a-time and Sobol analysis of nine factors, station vs ERA5 irradiation, clipping.
2. **Field validation (2025-2026)**: model with the as-built layout compared with AC power measured at the common output of the three inverters, and closure of the uncertainty budget.

**Important:** the annual energy (195 MWh, 1399 kWh/kWp) is a *modeled* value for 2023 weather, not measured production. On two clear days in October 2026 the plant delivered about 81 % of the modeled energy (see the paper). Do not use this ratio as an annual correction.

## Plant and model
- 372 AJP-S672-375 modules (139.5 kWp), tilt 23 deg, south, 24.066 N, 120.559 E (`src/config.py`).
- 1x30 kW and 2x50 kW inverters. As-built modules per inverter: 145 / 140 / 87 (used in the validation). The annual analysis uses two admissible layouts (scenarios a, b); the as-built layout changes the annual energy by +0.02 %.
- Chain: solar position -> Erbs -> Perez (albedo 0.25) -> Ross cell temperature (NOCT 46 C) -> PVWatts DC (8.7 % loss) -> inverter (constant, PVWatts-DS, PVWatts-G) -> sum of three inverters.
- Weather: CODiS station 467270 (Tianzhong, 21.4 km from the plant) and PVGIS-ERA5.

## Setup
Tested with Python 3.13.
```
pip install -r requirements.txt
```
Run every script from the repository root (for example `python src/val_analysis.py`).

## Part 1: annual analysis
```
python src/year2023.py                      # optional: rebuild data/processed/hourly_2023.csv from data/raw
python src/year_baseline.py                 # baseline, ERA5 vs station, clipping, per inverter (also runs year_compare.py)
OUTP=yr05 GHI_ERR=0.05 python src/run_sens_year.py    # OAT + Sobol, 11,264 runs (long; run in the background)
OUTP=yr10 GHI_ERR=0.10 python src/run_sens_year.py
python src/make_figs_year.py
python src/make_figs_sens_year.py
python src/fig_flow.py
```
Shipped `outputs/yr*` are the values used in the paper.

## Part 2: field validation
```
python src/val_analysis.py     # as-built model for 9 days + variants -> outputs/validation/*.csv   (about 15 s)
python src/val_stats.py        # numbers quoted in the paper
python src/val_stats2.py       # clear-sky fraction, steady-hour checks
python src/val_figures.py      # validation figures -> paper_figs/
```
Re-running `val_analysis.py` reproduces the shipped `outputs/validation/*.csv` exactly (maximum difference 0).

Measurement processing: `src/hioki_to_minute.py` converts Hioki MR8875 CSV files (currents CH1-1..1-3, line-to-line voltages CH2-1..2-3) to one-minute power.
Active power uses the two-wattmeter (Aron) method for a three-wire system, P = <v_ab i_a - v_bc i_c> averaged over the interval (the three cyclic forms agree within 1 %).
**Do not** sum v_k i_k with line-to-line voltages as if they were phase voltages; this overstates the power by about 1.5.

## Files
| Path | Content |
|---|---|
| `src/config.py` | all plant parameters, DC loss, mapping scenarios |
| `src/weather.py`, `src/cwa_month.py` | location, CODiS readers |
| `src/pv_model.py`, `src/inverter_model.py` | DC chain; inverter formulations (checked against `pvlib.inverter.pvwatts`) |
| `src/year*.py`, `src/sens_year.py`, `src/run_sens_year.py` | annual analysis and sensitivity |
| `src/val_*.py`, `src/hioki_to_minute.py` | field validation and Hioki processing |
| `data/processed/hourly_2023.csv` | hourly GHI (station, ERA5), Gb, Gd (ERA5), air temperature, 2023 |
| `data/validation/hioki_minute_*.csv` | one-minute AC power: main record (16-19 Oct 2026) and seven shorter records |
| `data/validation/codis_days/` | CODiS hourly tables for the nine validation days |
| `outputs/yr*` | annual results |
| `outputs/validation/` | validation results (`minute_all.csv`, `hourly_variants.csv`, `campaign_summary.csv`, ...) |
| `paper_figs/` | figures of the paper |

Raw Hioki waveforms (2 ms sampling, several hundred files) are not included; they are available on request.

## Limitations
- Two full days and seven two-hour records, mostly autumn; the measurement chain was not calibrated (checked only against one inverter display reading and the power factor).
- Only the combined AC output of the three inverters was measured; DC losses, inverter efficiency and the individual inverters cannot be separated.
- Irradiation comes from a station 21 km away; no pyranometer on the roof.
- Annual analysis: one year (2023), one station, one ERA5 cell; GHI error ranges (+-5 %, +-10 %) are assumptions; the ranking of factors depends on the assumed ranges.
- The causes of the remaining shortfall (shading, soiling, string mismatch, de-rating, outages) are hypotheses and have not been tested.

## License
Code: MIT (see `LICENSE`). Weather data remain under the terms of CWA (CODiS) and the European Commission JRC (PVGIS).
