# Calibration files (CCF): diagnosis and download

The SAS response tasks (`rmfgen`, `arfgen`, and `backscale`, which calls `arfgen`) read many
Current Calibration Files that the event-cleaning steps of Part A never touched. If even
one is missing, the task stops with

```
Could not open file 'EPN_TIMECORR_0011.CCF' for reading in:
  /home/<user>/sas/SPASE/CCF
```

and you only learn about the next missing file after fixing this one. These scripts find
all missing files at once and download them with progress output.

## Scripts

| Script | What it does |
|---|---|
| `check_missing_ccf.sh` | Pulls every `*_NNNN.CCF` name out of `ccf.cif`, keeps the `EPN_`, `XRT3_` and `XMM_` files, and reports which are missing or empty in `$SAS_CCFPATH`. The missing names are written to `lists/ccf_missing.txt`. With an argument, it checks that list instead. |
| `download_ccf.sh` | Downloads a list of CCFs from the HEASARC mirror. It skips files already on disk, asks the server for every size and prints the total, then shows a progress bar per file and a running `overall: X of Y, Ns elapsed, i/N files` line. It writes to `.part` first and renames only on success, then prints a summary with any failures. |
| `download_ccf_basic.sh` | The first, simpler version: downloads the list and keeps `download_success.txt` and `download_failed.txt` records. |

All three read `SPASE` (default `~/sas/SPASE`), `SAS_CCF` and `SAS_CCFPATH`, so nothing is
hard-coded to one machine.

## Typical use

```bash
source ../config/sas_env.sh
./check_missing_ccf.sh                         # scan the index
./download_ccf.sh lists/ccf_missing.txt        # fetch what is missing
./check_missing_ccf.sh                         # should print "check done"
```

## Lists

| File | Content |
|---|---|
| `lists/ccf_partc_needed.txt` | 32 CCFs required for the pn spectra and responses |
| `lists/ccf_list_small.txt` | the same without `EPN_FWC_0005.CCF` (606 MB filter-wheel-closed data, not needed here) |
| `lists/ccf_missing_final.txt` | the two mirror files found only by the full index scan |

`ccf_all_in_cif.txt`, `ccf_wanted.txt` and `ccf_missing.txt` are recreated by `check_missing_ccf.sh` on every run.

## Logs from the actual run

| Log | Step |
|---|---|
| `logs/01_cifbuild_unexpected_eof.log` | `cifbuild` fails on the truncated ODF summary file, so the Part A `ccf.cif` is reused |
| `logs/02_missing_ccf_check.log` | the first check flags 23 missing files, and `arfgen` stops on `EPN_TIMECORR_0011.CCF` |
| `logs/03_download_ccf_progress.log` | 15 files (279 MB) downloaded in 1857 s with progress output |
| `logs/04_ccf_cif_scan_and_final_download.log` | the full scan of 129 entries finds `XRT3_XAREAEF_0014` and `XRT3_XENCIREN_0003`, which are then downloaded |
| `logs/05_responses_generated.log` | `pn_src.rmf`, `pn_src.arf` and `pn_src_grp.pi` written |
