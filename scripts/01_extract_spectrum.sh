#!/bin/bash
# Part C: EPIC-pn source/background spectra, RMF, ARF and grouping
# 3C 111, XMM-Newton obs. 0552180101 (pn Prime Small Window)
set -e
cd ~/sas/SPASE/part_c
export SAS_CCFPATH=$HOME/sas/SPASE/CCF
export SAS_CCF=$HOME/sas/SPASE/ccf.cif
export SAS_ODF=$PWD/1683_0552180101_SCX00000SUM.SAS
mkdir -p figures/raw

EVT=pn_clean.fits                               # cleaned pn events (Part A)
GTI="gti($EVT:GTI00003,TIME)"                   # flare-filtered GTI, 60.3 ks
SRC="(X,Y) IN circle(27308.7,27578.4,600)"      # source, r = 30 arcsec (Part A)
BKG="(X,Y) IN circle(25689,24313,800)"          # background, r = 40 arcsec (Part A)
SEL="(CCDNR==4)&&(FLAG==0)&&(PATTERN<=4)"

rm -f pn_src_spec.pi pn_bkg_spec.pi pn_src.rmf pn_src.arf pn_src_grp.pi pn_src_all.fits

# pile-up check (all patterns)
evselect table=$EVT:EVENTS withfilteredset=yes filteredset=pn_src_all.fits destruct=yes \
  keepfilteroutput=yes expression="(CCDNR==4)&&(FLAG==0)&&($SRC)&&$GTI"
epatplot set=pn_src_all.fits plotfile=figures/raw/fig06_epatplot.ps useplotfile=yes
# SAS 22 epatplot writes figures/raw/fig06_epatplot.pdf directly; 03_make_plots.py restyles it as figures/fig06_pattern_fractions.pdf

# source and background spectra (standard pn channel range)
evselect table=$EVT:EVENTS withspectrumset=yes spectrumset=pn_src_spec.pi energycolumn=PI \
  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 \
  expression="$SEL&&($SRC)&&$GTI"
evselect table=$EVT:EVENTS withspectrumset=yes spectrumset=pn_bkg_spec.pi energycolumn=PI \
  spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 \
  expression="$SEL&&($BKG)&&$GTI"

# area scaling, responses, grouping (>= 25 counts/bin, oversample 3)
backscale spectrumset=pn_src_spec.pi badpixlocation=$EVT
backscale spectrumset=pn_bkg_spec.pi badpixlocation=$EVT
rmfgen spectrumset=pn_src_spec.pi rmfset=pn_src.rmf withenergybins=yes energymin=0.1 energymax=12 nenergybins=2400
arfgen spectrumset=pn_src_spec.pi arfset=pn_src.arf withrmfset=yes rmfset=pn_src.rmf \
  badpixlocation=$EVT detmaptype=psf
specgroup spectrumset=pn_src_spec.pi mincounts=25 oversample=3 rmfset=pn_src.rmf \
  arfset=pn_src.arf backgndset=pn_bkg_spec.pi groupedset=pn_src_grp.pi
