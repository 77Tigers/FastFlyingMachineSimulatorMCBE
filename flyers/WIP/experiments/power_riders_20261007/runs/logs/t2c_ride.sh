#!/usr/bin/env bash
# Requires Bash (Git Bash on Windows). Paths are resolved from this script.
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../../../.." && pwd -P)"
cd "${REPO_ROOT}/flyers/WIP/experiments/power_riders_20261007"
run() { echo "## $*"; python front_pr.py "$@" 2>&1 | grep -E "^\{|^built|Traceback|Error|FOUND|saved|max load" ; }
for c in K4 K1p; do for w in mwwm wmwm mwmw mmww wwmm wmmw; do
  run 7 --w $w --k4 nb1 --k5 nb1 --ride 1:V:$c --tl 120 --tag t2c_ride_${c}_$w; done; done
echo BATCH DONE
