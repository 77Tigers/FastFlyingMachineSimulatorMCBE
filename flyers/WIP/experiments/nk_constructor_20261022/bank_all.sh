#!/bin/sh
# bank the current best N_k flyer for every k (k=6 skipped: bank/pl26/n6_screw_ring_3p75 is better)
cd "$(dirname "$0")/../../../.."
for k in 3 4 5 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24; do
  echo "== k=$k"
  python scripts/bank_add.py flyers/WIP/experiments/nk_constructor_20261022/out/best/n$k.flyer --name nk_square_n$k 2>&1 | tail -3
done
echo ALLDONE
