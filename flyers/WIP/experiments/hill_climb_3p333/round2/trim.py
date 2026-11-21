"""Test permanent-cell removals on seed zero using the real simulator."""

import re
import subprocess
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from assemble import BIN, HERE, assemble


def trial(work, lines, limit):
    geometry, flyer = work / "edit.txt", work / "edit.flyer"
    geometry.write_text("\n".join(lines) + "\n")
    with redirect_stdout(StringIO()):
        assemble(geometry, flyer, limit)
    audit = subprocess.check_output(
        [BIN / "fastflyer-research", "audit", flyer, "120", "0"], text=True
    )
    fields = dict(re.findall(r"(\w+)=(-?\d+)", audit))
    return int(fields["distance"]) == 40 and all(
        int(fields[k]) == 0
        for k in (
            "extension_failures",
            "movement_failures",
            "conservation_mismatch_ticks",
        )
    )


def run(path):
    rows = path.read_text().splitlines()
    _, limit = map(int, rows[0].split())
    with TemporaryDirectory(dir=HERE) as tmp:
        candidates = [j for j, line in enumerate(rows) if line.split()[1] in ("G", "R")]
        wins = []
        for j in candidates:
            if trial(Path(tmp), rows[:j] + rows[j + 1 :], limit):
                wins.append(rows[j])
        print(path.name, "single removals", len(candidates), "clean", wins)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        run(Path(arg))
