"""Measure bank speeds offline; the viewer never benchmarks during browsing."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TICKS = 10_000

def engine_fingerprint(root: Path) -> str:
    digest = sha256()
    paths = sorted((root / "src").rglob("*.rs"))
    paths += [path for path in (root / "Cargo.toml", root / "Cargo.lock") if path.exists()]
    for path in paths:
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        # Windows checkouts may use CRLF while GitHub's Linux runner uses LF.
        digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticks", type=int, default=DEFAULT_TICKS)
    args = parser.parse_args()
    if args.ticks <= 0:
        parser.error("--ticks must be positive")
    paths = sorted((ROOT / "flyers/bank").rglob("*.flyer"))
    subprocess.run(["cargo", "build", "--release", "--bin", "fastflyer-bank-stats"], cwd=ROOT, check=True)
    binary = ROOT / "target/release" / ("fastflyer-bank-stats.exe" if os.name == "nt" else "fastflyer-bank-stats")
    output = subprocess.check_output([str(binary), str(args.ticks), *map(str, paths)], cwd=ROOT, text=True)
    entries = {}
    for line in output.splitlines():
        index, distance, extensions, failures, conserved = line.split("\t")
        path = paths[int(index)]
        entries[path.relative_to(ROOT).as_posix()] = {
            "sha256": sha256(path.read_bytes()).hexdigest(),
            "ticks": args.ticks,
            "distance": int(distance),
            "speed_bps": int(distance) * 10 / args.ticks,
            "extensions": int(extensions),
            "extension_failures": int(failures),
            "endpoint_conserved": conserved == "true",
        }
    result = {"format_version": 1, "engine_sha256": engine_fingerprint(ROOT), "ticks_per_second": 10, "entries": entries}
    destination = ROOT / "flyers/bank/catalogue.json"
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Measured {len(entries)} flyers for {args.ticks:,} ticks each: {destination}")


if __name__ == "__main__":
    main()
