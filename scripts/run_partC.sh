#!/bin/bash
# Part C runner: XSPEC fit -> PDF figures -> parameter table
cd ~/sas/SPASE/part_c || exit 1
mkdir -p results figures/raw
rm -f results/xspec_partC.log results/fit_results.txt results/best_fit_m*.xcm \
      results/qdp_*.qdp figures/raw/fig0[1-5]_*.ps figures/raw/fig0[1-5]_*.pdf
xspec <<< "@scripts/02_fit_spectrum.xcm"
for f in figures/raw/fig0[1-5]_*.ps; do ps2pdf "$f" "${f%.ps}.pdf"; done
python scripts/03_make_plots.py
python scripts/04_results_table.py
