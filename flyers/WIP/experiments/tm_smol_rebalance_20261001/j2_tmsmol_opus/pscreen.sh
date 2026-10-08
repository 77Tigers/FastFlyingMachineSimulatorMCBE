#!/bin/bash
# usage: pscreen.sh SRCDIR TICKS NSHARDS  -> shards SRCDIR/_sN, results SRCDIR.csv (merged)
SRC=$1; T=$2; N=${3:-16}
RUN=/c/Users/Ruben/OneDrive/Documents/FastFlyerPlayground/target/release/fastflyer-research
i=0
for f in $(find $SRC -name '*.flyer' -not -path '*/_s*'); do s=$((i % N)); mkdir -p $SRC/_s$s; mv $f $SRC/_s$s/; i=$((i+1)); done
for s in $(seq 0 $((N-1))); do [ -d $SRC/_s$s ] && $RUN screen $SRC/_s$s $T --out $SRC/_s$s.csv > /dev/null 2>&1 & done
wait
head -1 $SRC/_s0.csv > $SRC.csv; for s in $(seq 0 $((N-1))); do [ -f $SRC/_s$s.csv ] && tail -n +2 $SRC/_s$s.csv >> $SRC.csv; done
echo "screened $(($(wc -l < $SRC.csv)-1))"
