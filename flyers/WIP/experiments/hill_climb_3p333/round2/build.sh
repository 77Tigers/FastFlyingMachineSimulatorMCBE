#!/bin/sh
set -eu
cd "$(dirname "$0")"
cc -O3 -fPIC -c ../round1/route.c -o route.o
cc -O3 -fPIC -c profile.c -o profile.o
if command -v g++ >/dev/null; then
    g++ -std=c++17 -O3 ring.cpp route.o profile.o -o ring
else
    docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" -w /work golang:1.26-bookworm g++ -std=c++17 -O3 ring.cpp route.o profile.o -o ring
fi
