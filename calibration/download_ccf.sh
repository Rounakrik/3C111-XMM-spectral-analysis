#!/bin/bash
# =====================================================================
# download_ccf.sh
# CCF downloader with progress reporting.
#
#  * skips files that are already present and non-empty (safe to re-run)
#  * asks the server for every file size first and prints the total
#  * shows a curl progress bar for each file
#  * after each file prints: time taken, bytes done / bytes total,
#    elapsed time and files done / files total
#  * downloads to <name>.part and renames only on success, so an
#    interrupted run never leaves a truncated CCF behind
#  * prints a summary and the list of failed files at the end
#
# Usage:  ./download_ccf.sh [list_file]
#   list_file   one CCF name per line (default: lists/ccf_list_small.txt)
#
# Environment:
#   SPASE        project root            (default: $HOME/sas/SPASE)
#   SAS_CCFPATH  where CCFs are stored   (default: $SPASE/CCF)
# =====================================================================

HERE="$(cd "$(dirname "$0")" && pwd)"
SPASE="${SPASE:-$HOME/sas/SPASE}"
LIST="$(realpath "${1:-$HERE/lists/ccf_list_small.txt}")"
DEST="${SAS_CCFPATH:-$SPASE/CCF}"
BASE="https://heasarc.gsfc.nasa.gov/FTP/xmm/data/CCF"
mkdir -p "$DEST"
cd "$DEST" || exit 1
rm -f *.part

# collect the files still needed
TODO=()
while read -r f; do
  [ -z "$f" ] && continue
  [ -s "$f" ] || TODO+=("$f")
done < "$LIST"
N=${#TODO[@]}
echo "Files still to download: $N"
[ "$N" -eq 0 ] && { echo "Nothing to do."; exit 0; }

# ask the server for sizes
echo "Checking file sizes..."
declare -A SIZE
TOTAL=0
for f in "${TODO[@]}"; do
  s=$(curl -sIL "$BASE/$f" | grep -i '^content-length' | tail -1 | tr -dc '0-9')
  SIZE[$f]=${s:-0}
  TOTAL=$((TOTAL + ${s:-0}))
done
echo "Total to download: $(numfmt --to=iec --suffix=B $TOTAL)"
echo

START=$(date +%s)
DONE_BYTES=0
i=0
FAILED=()
for f in "${TODO[@]}"; do
  i=$((i+1))
  echo "=== [$i/$N] $f  ($(numfmt --to=iec --suffix=B ${SIZE[$f]})) ==="
  T0=$(date +%s)
  if curl -fL --retry 3 --progress-bar -o "$f.part" "$BASE/$f"; then
    mv "$f.part" "$f"
    DONE_BYTES=$((DONE_BYTES + $(stat -c%s "$f")))
    T1=$(date +%s)
    el=$((T1-T0)); tot=$((T1-START))
    echo "  done in ${el}s"
    echo "  overall: $(numfmt --to=iec --suffix=B $DONE_BYTES) of $(numfmt --to=iec --suffix=B $TOTAL), ${tot}s elapsed, $i/$N files"
  else
    rm -f "$f.part"; FAILED+=("$f"); echo "  FAILED: $f"
  fi
  echo
done

echo "========== SUMMARY =========="
echo "Downloaded: $((N - ${#FAILED[@]})) of $N files, $(numfmt --to=iec --suffix=B $DONE_BYTES)"
echo "Total time: $(( $(date +%s) - START ))s"
[ ${#FAILED[@]} -gt 0 ] && { echo "FAILED:"; printf '  %s\n' "${FAILED[@]}"; }
exit 0
