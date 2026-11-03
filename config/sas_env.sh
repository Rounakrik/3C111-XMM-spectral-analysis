# Source this file before running anything:  source config/sas_env.sh
# Edit SPASE if your project lives somewhere else.
export SPASE="${SPASE:-$HOME/sas/SPASE}"
export SAS_CCFPATH=$SPASE/CCF                 # calibration files
export SAS_CCF=$SPASE/ccf.cif                 # calibration index from Part A
export SAS_ODF=$SPASE/part_c/1683_0552180101_SCX00000SUM.SAS
echo "SAS_CCFPATH = $SAS_CCFPATH"
echo "SAS_CCF     = $SAS_CCF"
echo "SAS_ODF     = $SAS_ODF"
