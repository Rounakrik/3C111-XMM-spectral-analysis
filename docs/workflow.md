# Workflow and file dependencies

| Step | Command | Reads | Writes |
|---|---|---|---|
| 0 | `source config/sas_env.sh` | — | SAS environment variables |
| 1 | `calibration/check_missing_ccf.sh` | `ccf.cif`, `CCF/` | `calibration/lists/ccf_missing.txt` |
| 2 | `calibration/download_ccf.sh <list>` | CCF list | `CCF/*.CCF` |
| 3 | `scripts/01_extract_spectrum.sh` | `pn_clean.fits` (Part A) | `pn_src_spec.pi`, `pn_bkg_spec.pi`, `pn_src.rmf`, `pn_src.arf`, `pn_src_grp.pi`, `figures/raw/fig06_epatplot.pdf` |
| 4 | `xspec <<< "@scripts/02_fit_spectrum.xcm"` | `pn_src_grp.pi` (+ RMF, ARF, BKG via header) | `results/fit_results.txt`, `results/best_fit_m*.xcm`, `results/qdp_*.qdp`, `results/xspec_partC.log` |
| 5 | `python scripts/03_make_plots.py` | `results/qdp_*.qdp`, `figures/raw/fig06_epatplot.pdf` | `figures/fig01–06.{pdf,png}`, `results/epatplot_fractions.csv` |
| 6 | `python scripts/04_results_table.py` | `results/fit_results.txt` | `results/best_fit_table.{md,tex}` |
| 7 | `xspec <<< "@scripts/05_diagnostics.xcm"` | `pn_src_grp.pi` | `results/diagnostics.txt`, `results/xspec_diagnostics.log` |
| 8 | `pdflatex report/report_partC.tex` (×2) | `figures/`, `scripts/` | `report/report_partC.pdf` |

Steps 4–6 are wrapped in `scripts/run_partC.sh`.

## Extraction settings

| Setting | Value |
|---|---|
| Source region | circle, r = 30″ (600 sky pixels), from Part A |
| Background region | circle, r = 40″, same CCD, from Part A |
| Event selection | `CCDNR==4 && FLAG==0 && PATTERN<=4`, flare-filtered GTI (60.3 ks) |
| RMF | 2400 bins, 0.1–12 keV |
| ARF | `detmaptype=psf` (point source, θ = 67.9″) |
| Grouping | ≥ 25 counts per bin, oversample = 3 |

## Fit settings

| Setting | Value |
|---|---|
| Band | 0.3–10 keV |
| Absorption | `tbabs`, `abund wilm`, `xsect vern` |
| Models | `tbabs*zpowerlw`, `tbabs*(zpowerlw+zgauss)`, z = 0.049 |
| Unabsorbed flux and luminosity | `cflux`, `clumin` |
| Cosmology | `cosmo 70 0 0.73` |
| Errors | 90 %, Δχ² = 2.706 (`error maximum 10.0`) |
