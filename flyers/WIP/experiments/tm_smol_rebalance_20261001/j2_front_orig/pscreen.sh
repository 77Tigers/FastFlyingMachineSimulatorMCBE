#!/usr/bin/env bash
# Requires Bash (Git Bash on Windows). usage: pscreen.sh SRCDIR TICKS [NSHARDS]
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../../.." && pwd -P)"
SRC=$1; T=$2; N=${3:-16}
RUN="$REPO_ROOT/target/release/fastflyer-research"
case "${OSTYPE:-}" in msys*|cygwin*) RUN+=.exe ;; esac
i=0
while IFS= read -r -d '' f; do
  s=$((i % N)); mkdir -p "$SRC/_s$s"; mv -- "$f" "$SRC/_s$s/"; i=$((i+1))
done < <(find "$SRC" -name '*.flyer' -not -path '*/_s*' -print0)
for ((s=0; s<N; s++)); do
  if [[ -d "$SRC/_s$s" ]]; then
    "$RUN" screen "$SRC/_s$s" "$T" --out "$SRC/_s$s.csv" >/dev/null 2>&1 &
  fi
done
wait
head -1 "$SRC/_s0.csv" > "$SRC.csv"
for ((s=0; s<N; s++)); do
  [[ ! -f "$SRC/_s$s.csv" ]] || tail -n +2 "$SRC/_s$s.csv" >> "$SRC.csv"
done
echo "screened $(($(wc -l < "$SRC.csv")-1))"
