#!/bin/bash
# Requires Bash (Git Bash on Windows). Paths are resolved from this script.
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../../.." && pwd -P)"
EXE_SUFFIX=
case "${OSTYPE:-}" in msys*|cygwin*) EXE_SUFFIX=.exe ;; esac
cd "${REPO_ROOT}"
W=flyers/WIP/experiments/pl11_3bps_20261013/front_orig_cap11
i=1
for cfg in "1 bounded" "2 bounded" "3 advance"; do
  set -- $cfg
  "${REPO_ROOT}/target/release/contract-search${EXE_SUFFIX}" $W/before_natural.json 1200 6 $W/run$i --seed $1 --margin 2 --order both --recurrence $2 --target 11 --rank endogenous > $W/run$i.log 2>&1
  i=$((i+1))
done
echo done > $W/runs.done
