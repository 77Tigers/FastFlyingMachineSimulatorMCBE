#!/bin/sh
set -eu
cd "$(dirname "$0")"
if ! command -v g++ >/dev/null; then
    climb=$(cd .. && pwd)
    exec docker run --rm --network none -u "$(id -u):$(id -g)" \
        -v "$climb:/climb:ro" -v "$climb/round5:/climb/round5" \
        -w /climb/round5 golang:1.26-bookworm sh build.sh "$@"
fi
if [ "$#" -eq 0 ]; then
    set -- handoff back mixed spine ring towers
fi
cc -O3 -c ../round1/route.c -o route.o
for name in "$@"; do
    g++ -std=c++17 -O3 "$name.cpp" route.o -o "$name"
done
