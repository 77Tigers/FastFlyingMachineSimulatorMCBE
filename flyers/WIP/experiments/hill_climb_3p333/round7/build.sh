#!/bin/sh
set -eu
cd "$(dirname "$0")"
if ! command -v g++ >/dev/null; then
    climb=$(cd .. && pwd)
    exec docker run --rm --network none -u "$(id -u):$(id -g)" \
        -v "$climb:/climb:ro" -v "$climb/round7:/climb/round7" \
        -w /climb/round7 golang:1.26-bookworm sh build.sh "$@"
fi
for program do
    case "$program" in
        world) g++ -std=c++17 -O3 -Wall -Wextra world.cpp -o world ;;
        offsets) g++ -std=c++17 -O3 -Wall -Wextra offsets.cpp -o offsets ;;
        discovery) g++ -std=c++17 -O3 -Wall -Wextra -shared -fPIC discovery.cpp -o discovery.so ;;
        port_sweep) g++ -std=c++17 -O3 -Wall -Wextra port_sweep.cpp -o port_sweep ;;
        links)
            cc -O3 -c ../round1/route.c -o route.o
            cc -O3 -c ../round2/profile.c -o profile.o
            g++ -std=c++17 -O3 links.cpp route.o profile.o -o links ;;
        *) exit 2 ;;
    esac
done
