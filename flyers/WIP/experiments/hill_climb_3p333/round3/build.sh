#!/bin/sh
set -eu
cd "$(dirname "$0")"
if ! command -v g++ >/dev/null; then
    exec docker run --rm -u "$(id -u):$(id -g)" -v "$(cd .. && pwd):/climb" \
        -w /climb/round3 golang:1.26-bookworm sh build.sh
fi
cc -O3 -c ../round1/route.c -o route.o
cc -O3 -c ../round2/profile.c -o profile.o
for program in back towers; do
    g++ -std=c++17 -O3 "$program.cpp" route.o profile.o -o "$program"
done
