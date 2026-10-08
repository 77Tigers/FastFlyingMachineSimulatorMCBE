#!/bin/bash
# verify_speed.sh FLYER LIMIT PERIOD : 80-case full 10000-tick speed/conservation sample at the encoded LIMIT (tools bin sol-samples; cargo build --release --manifest-path tools/Cargo.toml --target-dir target)
set -e
D=$(cd "$(dirname "$0")" && pwd)
F=$1; L=$2; P=${3:-10}
python "$D/setlimit.py" "$F" "$L" "${F%.flyer}_pl$L.flyer" >/dev/null
S="$D/../../../../target/release/sol-samples"; [ -e "$S.exe" ] && S="$S.exe"
"$S" "${F%.flyer}_pl$L.flyer" $P > "${F%.flyer}_pl$L.samples.csv"
awk -F, 'NR>1{d[$5","$6","$7]++}END{for(k in d)print "distance,failures,conserved:",k,"cases",d[k]}' "${F%.flyer}_pl$L.samples.csv"
