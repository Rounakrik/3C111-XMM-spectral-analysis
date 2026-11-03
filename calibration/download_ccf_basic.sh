#!/bin/bash
# =====================================================================
# download_ccf_basic.sh
# First version of the CCF downloader (used in Part B and reused here).
# Reads a list of CCF file names, downloads each one from the HEASARC
# mirror and keeps two record files: one for successes, one for failures.
#
# Usage:  ./download_ccf_basic.sh [list_file]
#   list_file   one CCF name per line (default: lists/ccf_partc_needed.txt)
#
# Environment:
#   SPASE        project root            (default: $HOME/sas/SPASE)
#   SAS_CCFPATH  where CCFs are stored   (default: $SPASE/CCF)
# =====================================================================

HERE="$(cd "$(dirname "$0")" && pwd)"
SPASE="${SPASE:-$HOME/sas/SPASE}"
LIST="${1:-$HERE/lists/ccf_partc_needed.txt}"
DEST="${SAS_CCFPATH:-$SPASE/CCF}"
BASE="https://heasarc.gsfc.nasa.gov/FTP/xmm/data/CCF"

mkdir -p "$DEST"
FAILED="$DEST/download_failed.txt"
SUCCESS="$DEST/download_success.txt"

: > "$FAILED"
: > "$SUCCESS"

while IFS= read -r FILE; do
    [ -z "$FILE" ] && continue

    echo
    echo "Downloading $FILE"

    if curl -fL --retry 3 --connect-timeout 30 \
        --output "$DEST/$FILE.part" "$BASE/$FILE"; then

        if [ -s "$DEST/$FILE.part" ]; then
            mv "$DEST/$FILE.part" "$DEST/$FILE"
            echo "$FILE" >> "$SUCCESS"
            echo "SUCCESS: $FILE"
        else
            rm -f "$DEST/$FILE.part"
            echo "$FILE" >> "$FAILED"
            echo "EMPTY FILE: $FILE"
        fi
    else
        rm -f "$DEST/$FILE.part"
        echo "$FILE" >> "$FAILED"
        echo "FAILED: $FILE"
    fi

done < "$LIST"

echo
echo "========== DOWNLOAD SUMMARY =========="
echo "Requested: $(grep -cve '^[[:space:]]*$' "$LIST")"
echo "Downloaded: $(wc -l < "$SUCCESS")"
echo "Failed: $(wc -l < "$FAILED")"
echo "Directory size:"
du -sh "$DEST"
