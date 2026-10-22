#!/bin/bash
# Requires Bash (Git Bash on Windows). Paths are resolved from this script.
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../../.." && pwd -P)"
EXE_SUFFIX=
case "${OSTYPE:-}" in msys*|cygwin*) EXE_SUFFIX=.exe ;; esac
# usage: ev.sh DIR [TICKS] [LIMIT]
T="${REPO_ROOT}/flyers/WIP/experiments/tm_smol_rebalance_20261001"
L="$REPO_ROOT/target/release/loadhist$EXE_SUFFIX"
"$L" ${2:-600} 100 ${3:-24} "$1"/c*.flyer
