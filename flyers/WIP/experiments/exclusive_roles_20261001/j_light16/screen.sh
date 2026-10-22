#!/bin/bash
# Requires Bash (Git Bash on Windows). Paths are resolved from this script.
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../../.." && pwd -P)"
# usage: screen.sh DIR  -> prints file distance/ext_fail/move_fail for each c*.flyer (limit stored in file)
B="${REPO_ROOT}/target/release"
for f in "$1"/c*.flyer; do
 r=$("$B/fastflyer-research" measure "$f" 1000 10 2>&1 | head -1)
 echo "$f $(echo "$r" | grep -o 'distance=[0-9-]*\|extension_failures=[0-9]*\|movement_failures=[0-9]*\|first_failure_tick=[^ ]*' | tr '\n' ' ')"
done
