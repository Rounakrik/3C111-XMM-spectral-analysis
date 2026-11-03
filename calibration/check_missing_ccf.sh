#!/bin/bash
# =====================================================================
# check_missing_ccf.sh
# Diagnosis of missing Current Calibration Files (CCFs).
#
# rmfgen/arfgen stop with "Could not open file 'XXX.CCF' for reading"
# when a CCF listed in the calibration index is not on disk. This script
# finds every such file before running SAS, instead of one per crash.
#
# Two modes:
#   ./check_missing_ccf.sh                  scan the calibration index
#   ./check_missing_ccf.sh <list_file>      check a given list of names
#
# Mode 1 (default) does what was done by hand during Part C:
#   1. pulls every *_NNNN.CCF name out of ccf.cif (binary FITS, so grep -a)
#   2. keeps the EPIC-pn (EPN_), mirror (XRT3_) and general (XMM_) files
#   3. drops EPN_FWC_0005.CCF (606 MB filter-wheel-closed data, not
#      needed for spectra or responses)
#   4. writes the names not found (or empty) in $SAS_CCFPATH to
#      ccf_missing.txt, which can be passed straight to download_ccf.sh
#
# Environment:
#   SPASE        project root            (default: $HOME/sas/SPASE)
#   SAS_CCF      calibration index       (default: $SPASE/ccf.cif)
#   SAS_CCFPATH  where CCFs are stored   (default: $SPASE/CCF)
# =====================================================================

HERE="$(cd "$(dirname "$0")" && pwd)"
SPASE="${SPASE:-$HOME/sas/SPASE}"
CIF="${SAS_CCF:-$SPASE/ccf.cif}"
CCFDIR="${SAS_CCFPATH:-$SPASE/CCF}"
OUT="$HERE/lists"
SKIP="EPN_FWC_0005.CCF"
mkdir -p "$OUT"

if [ -n "$1" ]; then
  # ---- mode 2: check a list -------------------------------------------
  WANTED="$1"
  echo "Checking list: $WANTED"
else
  # ---- mode 1: scan the calibration index ------------------------------
  [ -f "$CIF" ] || { echo "Calibration index not found: $CIF"; exit 1; }
  grep -a -o "[A-Z0-9_]*_[0-9]\{4\}\.CCF" "$CIF" | sort -u > "$OUT/ccf_all_in_cif.txt"
  echo "CCF entries in $(basename "$CIF"): $(wc -l < "$OUT/ccf_all_in_cif.txt")"
  grep -E "^(EPN|XRT3|XMM)_" "$OUT/ccf_all_in_cif.txt" | grep -v "^${SKIP}$" > "$OUT/ccf_wanted.txt"
  WANTED="$OUT/ccf_wanted.txt"
  echo "EPN/XRT3/XMM files needed (without $SKIP): $(wc -l < "$WANTED")"
fi

# ---- the actual check: missing or zero-size files ----------------------
: > "$OUT/ccf_missing.txt"
n_ok=0; n_miss=0
while read -r f; do
  [ -z "$f" ] && continue
  if [ -s "$CCFDIR/$f" ]; then
    n_ok=$((n_ok+1))
  else
    echo "MISSING $f"
    echo "$f" >> "$OUT/ccf_missing.txt"
    n_miss=$((n_miss+1))
  fi
done < "$WANTED"

echo
echo "========== CCF CHECK =========="
echo "Present : $n_ok"
echo "Missing : $n_miss"
if [ "$n_miss" -gt 0 ]; then
  echo "Missing names written to $OUT/ccf_missing.txt"
  echo "Download them with:  $HERE/download_ccf.sh $OUT/ccf_missing.txt"
else
  echo "check done: all calibration files are in place"
fi
