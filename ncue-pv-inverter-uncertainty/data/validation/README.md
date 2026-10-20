# Validation data
- `hioki_minute_oct2026.csv`: one-minute means of the main Hioki MR8875 record, 16 Oct 19:46 to 19 Oct 18:05, 2026 (time = start of the minute, Asia/Taipei). Columns: P_kW (two-wattmeter active power), I_rms_A, V_rms_V, pf, n_sampel (samples per minute), file.
- `hioki_minute_2025_records.csv`, `hioki_minute_2025_2026_records.csv`: one-minute means of the seven two-hour records (17 Jun, 7 Aug, 21 Dec 2025; 23 Oct, 27 Oct 2025; 10 Feb, 24 Apr 2026).
- `codis_days/`: hourly CODiS tables (station 467270) for the nine validation days. Source: Central Weather Administration, CODiS (https://codis.cwa.gov.tw/). Check the CWA terms of use before redistributing; remove this folder if redistribution is not allowed (the scripts then need the files downloaded by the user).
- The 27 Jul 2025 and 15 Mar 2026 records were not used (no station table / night record).
