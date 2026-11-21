#!/bin/sh
set -eu
cd "$(dirname "$0")"
if ! command -v g++ >/dev/null; then
    climb=$(cd .. && pwd)
    exec docker run --rm --network none -u "$(id -u):$(id -g)" \
        -v "$climb:/climb:ro" -v "$climb/round6:/climb/round6" \
        -w /climb/round6 golang:1.26-bookworm sh build.sh "$@"
fi
cc -O3 -c ../round1/route.c -o route.o
for program in "$@"; do
    g++ -std=c++17 -O3 "$program.cpp" route.o -o "$program"
done
