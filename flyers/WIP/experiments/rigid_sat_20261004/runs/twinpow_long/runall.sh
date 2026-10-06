cd /c/Users/Ruben/OneDrive/Documents/FastFlyerPlayground/flyers/WIP/experiments/rigid_sat_20261004
for cfg in "7 V" "7 none" "6 V" "6 none"; do set -- $cfg
  LOAD=7 python twinpow_long.py last$1_$2 $1 $2 120 7 7 7 1 all m3,1 4 4 > runs/twinpow_long/last$1_$2.out 2>&1
done
