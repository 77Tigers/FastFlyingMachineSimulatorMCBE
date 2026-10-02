#!/bin/bash
# usage: runshard.sh OUTDIR LIM RAILMAX CFG
cd /c/Users/Ruben/OneDrive/Documents/FastFlyerPlayground/flyers/WIP/experiments/tm_smol_rebalance_20261001/j_mmwmw2
ONLY=$4 PORTCAP=250 LIM=$2 RAILMAX=$3 NMAX=10 COMBOS=300 python selfpush2.py ../../exclusive_roles_20261001/human_base.flyer 5 $1 --cached > $1/log_${4//:/_}.txt 2>&1
