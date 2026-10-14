#!/bin/bash
# usage: runall.sh SRC [TAG]   (extract + publish)
cd "$(dirname "$0")"
src=$1; tag=${2:-$(basename "$src" .flyer)}
python extract.py "$src" --tag "$tag" && python publish.py "$tag"
