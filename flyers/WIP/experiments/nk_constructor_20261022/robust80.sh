#!/bin/sh
# 80 bank seeds, 1000 blocks, at the predicted PL (README table); reports pass at PL and at PL-1
PLS="3:18 4:21 5:26 6:28 7:33 8:36 9:39 10:43 11:46 12:50 13:52 14:57 15:60 16:64 17:68 18:71 19:75 20:78 21:79 22:85 23:87 24:90"
for e in $PLS; do
  k=${e%%:*}; pl=${e##*:}; P=$((2*(k+2))); n=$((1000/k+2))
  echo "k=$k $(./out/target/release/nkcheck.exe out/best/n$k.flyer $((n*P)) 1000 80 at $pl)"
done
