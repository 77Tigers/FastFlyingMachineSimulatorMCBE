#!/bin/sh
# Representative replay check of the Lean semantics against the Rust simulator.
# Run from the repository root after building both (see formal/README.md):
#   sh formal/replay_check.sh [TRACE_DIR]
# 9 bank flyers x 1000 ticks (state compared every 10 ticks) plus 4 runs with a push
# limit below the flyer's (failed moves, angry pistons). Traces of failures are kept.
set -u
D="${1:-${TMPDIR:-/tmp}/ff_replay}"
mkdir -p "$D"
fail=0
one() {
  b=$(basename "$1" .flyer)
  ./target/release/lean-replay-export "$1" 1000 "$D/$b.txt" 10 || { echo "EXPORT-FAIL $1"; fail=1; return; }
  r=$(./formal/.lake/build/bin/replay "$D/$b.txt")
  echo "${PUSH_LIMIT:+PL=$PUSH_LIMIT }$r"
  case "$r" in OK*) rm -f "$D/$b.txt" ;; *) fail=1 ;; esac
}
for f in pl3/compact_honey pl7/tm_7pl_2.5bps pl8/hop_pair_rod_observer pl9/pulling_loop4 \
         pl10/two_body_5slot_2bps pl12/human_3bps_original pl26/n6_screw_ring_3p75 \
         pl34/ab_push_pull_7body pl34/nk_lat_n8; do
  one "flyers/bank/$f.flyer"
done
for spec in "11 pl12/human_3bps_original" "6 pl7/tm_7pl_2.5bps" "2 pl34/ab_push_pull_7body" \
            "4 pl26/n6_screw_ring_3p75"; do
  set -- $spec
  PUSH_LIMIT=$1 one "flyers/bank/$2.flyer"
done
exit $fail
