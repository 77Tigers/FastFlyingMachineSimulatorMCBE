#!/bin/sh
# 80 bank seeds, 1000 blocks, at the predicted PL (pass at PL, and report whether PL-1 also passes)
for k in $(seq 3 24); do
  f=out/best/n$k.flyer
  pl=$(python -c "from fastflyer import Flyer; print(Flyer.load('$f').push_limit)")
  P=$((2*(k+2))); n=$((1000/k+2))
  echo "k=$k pl=$pl $(./out/target/release/nkcheck.exe $f $((n*P)) 1000 80 at $pl)"
done
