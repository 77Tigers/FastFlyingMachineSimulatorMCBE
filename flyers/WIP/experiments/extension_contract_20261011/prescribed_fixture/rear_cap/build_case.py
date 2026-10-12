"""Regenerate the two-input K1 phase-shift prescribed fixture contract."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PERIOD = 8
ADVANCE = 2
CYCLES = 3
PORTS = [
    {"name": "redstone_input", "role": "input", "at": [3, 2, 16],
     "word": "mmww", "limit": 1, "budget": [1, 1, None, None]},
    {"name": "k1_input", "role": "input", "at": [3, 1, 17],
     "word": "wwmm", "limit": 7, "budget": [None, None, 7, 7]},
]


def rows(cycles: int) -> list[tuple[int, str]]:
    result = []
    for cycle in range(cycles):
        for port in PORTS:
            moved = 0
            x = port["at"][0] + cycle * ADVANCE
            for slot, state in enumerate(port["word"]):
                if state == "m":
                    tick = cycle * PERIOD + 2 * slot
                    result.append((tick, f"{tick} {x} {port['at'][1]} {port['at'][2]} {port['limit']}"))
                    moved += 1
                    x += 1
            assert moved == port["word"].count("m")
            assert x == port["at"][0] + (cycle + 1) * ADVANCE
    assert len(result) == cycles * sum(port["word"].count("m") for port in PORTS)
    return sorted(result)


def main() -> None:
    subprocess.run([sys.executable, "-B", str(HERE / "build_fixture.py")],
                   cwd=ROOT, check=True)
    scheduled = rows(CYCLES)
    (HERE / "two_input_drive.txt").write_text(
        "\n".join(line for _, line in scheduled) + "\n", encoding="ascii")
    one_period = rows(1)
    (HERE / "two_input_oneperiod.txt").write_text(
        "\n".join(line for _, line in one_period) + "\n", encoding="ascii")
    contract = {
        "version": 1,
        "name": "pl7-rear-prescribed-redstone-and-k1-phase-shift-n-output",
        "flyer": "candidate.flyer",
        "prescribed_script": "two_input_drive.txt",
        "prescribed_order": "before_natural",
        "period_ticks": PERIOD,
        "advance": ADVANCE,
        "cycles": CYCLES,
        "recurrence": "bounded",
        "boundary_envelope": {"min": [0, 0, 15], "max": [9, 3, 18]},
        "ports": [
            {"name": "redstone_input", "role": "input", "at": [3, 2, 16],
             "word": "mmww", "baseline_load": PORTS[0]["budget"],
             "spare_load": [0, 0, None, None]},
            {"name": "k1_input", "role": "input", "at": [3, 1, 17],
             "word": "wwmm", "baseline_load": PORTS[1]["budget"],
             "spare_load": [None, None, 0, 0]},
            {"name": "k0_output", "role": "output", "at": [0, 1, 15], "word": "mmww"},
            {"name": "n_output", "role": "output", "at": [2, 0, 15], "word": "wmmw"},
        ],
    }
    (HERE / "two_input_contract.json").write_text(
        json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    print(f"generated {len(scheduled)} prescribed starts; "
          f"per-period move counts={[port['word'].count('m') for port in PORTS]}")


if __name__ == "__main__":
    main()
