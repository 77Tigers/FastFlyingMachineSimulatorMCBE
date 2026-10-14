#!/bin/bash
cd /c/Users/Ruben/OneDrive/Documents/FastFlyerPlayground
W=flyers/WIP/experiments/pl11_3bps_20261013/front_orig_cap11
i=1
for cfg in "1 bounded" "2 bounded" "3 advance"; do
  set -- $cfg
  target/release/contract-search.exe $W/before_natural.json 1200 6 $W/run$i --seed $1 --margin 2 --order both --recurrence $2 --target 11 --rank endogenous > $W/run$i.log 2>&1
  i=$((i+1))
done
echo done > $W/runs.done
