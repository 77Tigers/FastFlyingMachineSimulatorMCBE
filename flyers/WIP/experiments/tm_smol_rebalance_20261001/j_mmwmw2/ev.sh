#!/bin/bash
# usage: ev.sh DIR [TICKS] [LIMIT]
T=/c/Users/Ruben/OneDrive/Documents/FastFlyerPlayground/flyers/WIP/experiments/tm_smol_rebalance_20261001
$T/loadhist.exe ${2:-600} 100 ${3:-24} $1/c*.flyer
