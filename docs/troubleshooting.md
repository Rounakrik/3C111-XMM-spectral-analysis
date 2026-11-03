# Troubleshooting

These are the problems I met during Part C and how each one was solved.

## 1. `cifbuild`: `UnexpectedEOF ... of ODF summary file`

```
** cifbuild: error (UnexpectedEOF), Unexpected EOF in line #435 of ODF summary file
```

**Cause:** the `*SUM.SAS` file copied into `part_c/` was truncated.
**Fix:** reuse the calibration index from Part A. It was built for the observation date, so it is valid.

```bash
export SAS_CCF=$HOME/sas/SPASE/ccf.cif
```

## 2. `Could not open file 'XXX.CCF' for reading`

**Cause:** the CCF is listed in `ccf.cif` but is not in `$SAS_CCFPATH`.
**Fix:** run `calibration/check_missing_ccf.sh`, then `calibration/download_ccf.sh lists/ccf_missing.txt`. See [`calibration/README.md`](../calibration/README.md).

## 3. A very large CCF (`EPN_FWC_0005.CCF`, 606 MB)

The download was slow and the file is not needed for source spectra or responses, so it is excluded with
`ccf_list_small.txt`, and `check_missing_ccf.sh` skips it.

## 4. `epatplot`: `ps2pdf` fails

SAS 22 `epatplot` writes a **PDF** directly, even when `plotfile=*.ps` is given.
**Fix:** use `figures/raw/fig06_epatplot.pdf` as it is. `03_make_plots.py` reads the pattern fractions from its vector paths.

## 5. XSPEC: `Reduced Chi^2 > maximum (2)` in `error`

The full-band fit has χ²<sub>ν</sub> ≈ 2.3, so XSPEC refuses to compute errors by default.
**Fix:** `error maximum 10.0 2.706 <pars>` in `02_fit_spectrum.xcm`.

## 6. Matplotlib: `usetex` fails (no `cm-super`)

**Fix:** no LaTeX rendering; Computer Modern through `font.serif = cmr10` and `mathtext.fontset = "cm"`.

## 7. Reading the `epatplot` ratios

The clean event list keeps only `PATTERN<=4`, so the observed triple and quadruple fractions are zero, while the `epatplot`
model still expects about 2 % of them. This pushes both the single and the double ratios slightly above 1
(s = 1.026, d = 1.014), which is **not** pile-up. After renormalising the model to singles + doubles
(Fig. 6b), the ratios are 1.015 and 0.96: a small deficit of doubles, the opposite of what pile-up would do.
