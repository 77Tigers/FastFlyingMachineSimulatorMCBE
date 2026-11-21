"""Audit the saved flyer, its lower-limit control, and every single solid deletion."""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from fastflyer import Flyer, Kind

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "round3"))
from check import BIN, ledger


def audit(path, ticks):
    out = subprocess.check_output(
        [BIN / "fastflyer-research", "audit", path, str(ticks), "0"], text=True
    ).strip()
    stats = {k: int(v) for k, v in re.findall(r"(\w+)=(-?\d+)", out)}
    clean = all(
        stats[k] == 0
        for k in ("movement_failures", "extension_failures", "conservation_mismatch_ticks")
    )
    return stats, clean and stats["distance"] >= ticks // 3, out


def screen(path, scratch):
    flyer = Flyer.load(str(path))
    limit = flyer.push_limit
    for pl in (limit, limit - 1):
        for phase in (0, 7):
            flyer.push_limit = pl
            flyer.phase_x = flyer.phase_z = phase
            flyer.rng_state = 0
            flyer.save(str(scratch))
            for ticks in (240, 10_000):
                stats, passed, out = audit(scratch, ticks)
                print(out.replace(str(scratch), path.name))
                assert (stats["limit"], stats["phase_x"], stats["phase_z"]) == (pl, phase, phase)
                assert passed == (pl == limit)


def single_deletions(path, scratch):
    flyer = Flyer.load(str(path))
    flyer.phase_x = flyer.phase_z = flyer.rng_state = 0
    count = 0
    for pos, block in flyer.blocks():
        if block.kind in (Kind.SLIME, Kind.HONEY, Kind.REDSTONE_BLOCK):
            flyer.remove(pos)
            flyer.save(str(scratch))
            _, passed, _ = audit(scratch, 240)
            assert not passed, f"flyer still passes after deleting {block.kind.name} at {pos}"
            flyer.set(pos, block)
            count += 1
    print(f"all {count} single glue or redstone deletions failed the 240-tick flight screen")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("flyer", type=Path)
    parser.add_argument("geometry", type=Path)
    parser.add_argument("--slot", required=True, type=int, choices=range(6))
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(dir=HERE) as tmp:
        scratch = Path(tmp) / args.flyer.name
        screen(args.flyer, scratch)
        ledger(args.flyer, args.geometry, args.slot)
        single_deletions(args.flyer, scratch)
