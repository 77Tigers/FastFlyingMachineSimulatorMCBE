#!/bin/bash
# usage: ev.sh DIR [TICKS] [LIMIT]
T=/c/Users/Ruben/OneDrive/Documents/FastFlyerPlayground/flyers/WIP/experiments/tm_smol_rebalance_20261001
L=$T/../../../../target/release/loadhist; [ -e "$L.exe" ] && L=$L.exe
$L ${2:-600} 100 ${3:-24} $1/c*.flyer
