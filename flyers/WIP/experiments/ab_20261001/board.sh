#!/bin/bash
# audit all candidates in given dirs (cached), print leaderboard by max load
cd "$(dirname "$0")/.."
for d in "$@"; do
  for f in ab_20261001/$d/*.flyer; do
    [ -e "$f" ] || continue
    c="$f.audit"
    if [ ! -e "$c" ]; then ../../../target/release/fastflyer-research audit "$f" 600 10 | tail -1 > "$c"; fi
    echo "$(grep -oE 'max_successful_action=[0-9]+' $c | cut -d= -f2) $(grep -oE 'distance=[0-9]+' $c | cut -d= -f2) $f"
  done
done | sort -n | head -15
