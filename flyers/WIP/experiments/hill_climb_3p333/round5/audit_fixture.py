"""Compare the serialized local relay to its lower push-limit control."""

import re
import subprocess
import tempfile
from pathlib import Path

from fastflyer import Flyer

HERE = Path(__file__).resolve().parent
BIN = HERE.parents[4] / "target" / "release"
FIXTURE = HERE / "local_witness_pl13.fixture"


def main():
    flyer = Flyer.load(str(FIXTURE))
    assert flyer.push_limit == 13
    with tempfile.TemporaryDirectory(dir=HERE) as tmp:
        path = Path(tmp) / FIXTURE.name
        for limit in (13, 12):
            for phase in (0, 7):
                flyer.push_limit = limit
                flyer.phase_x = flyer.phase_z = phase
                flyer.rng_state = 0
                flyer.save(str(path))
                for ticks in (240, 10_000):
                    output = subprocess.check_output(
                        [BIN / "fastflyer-research", "audit", path, str(ticks), "0"],
                        text=True,
                    )
                    stats = {k: int(v) for k, v in re.findall(r"(\w+)=(-?\d+)", output)}
                    assert (stats["distance"], stats["conservation_mismatch_ticks"]) == (0, 0)
                    failures = ticks if limit == 12 else 0
                    assert stats["extension_failures"] == stats["movement_failures"] == failures
                    print(output.strip().replace(str(path), FIXTURE.name))


if __name__ == "__main__":
    main()
