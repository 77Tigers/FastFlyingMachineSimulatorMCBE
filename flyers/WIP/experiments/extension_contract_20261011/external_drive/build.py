"""Build three driven-slime-column fixtures for the external drive adapter."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT))

from fastflyer import Block, Flyer, Kind


DRIVER = ROOT / "target/release" / ("extension-drive.exe" if os.name == "nt" else "extension-drive")
CASES = {
    "mmmww": {"period": 10, "advance": 3, "ticks": [0, 2, 4], "rows_y": [0, 2, 0]},
    "mmmmww": {"period": 12, "advance": 4, "ticks": [0, 2, 4, 6], "rows_y": [0, 2, 0, 2]},
    "mmwmmw": {"period": 12, "advance": 4, "ticks": [0, 2, 6, 8], "rows_y": [0, 2, 0, 2]},
}


def ensure_driver() -> None:
    if DRIVER.is_file():
        return
    subprocess.run(
        ["cargo", "build", "--release", "--manifest-path", str(ROOT / "tools/Cargo.toml"),
         "--target-dir", str(ROOT / "target"), "--bin", "extension-drive"],
        cwd=ROOT,
        check=True,
    )
    if not DRIVER.is_file():
        raise RuntimeError(f"drive executable was not produced: {DRIVER}")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    ensure_driver()
    out = HERE / "out"
    scripts = HERE / "drives"
    contracts = HERE / "contracts"
    out.mkdir(exist_ok=True)
    scripts.mkdir(exist_ok=True)
    contracts.mkdir(exist_ok=True)

    flyer = Flyer(rng_state=5, phase_x=0, phase_z=0, push_limit=12)
    for y in range(3):
        flyer.set((0, y, 0), Block(Kind.SLIME))
    flyer_path = HERE / "driver.flyer"
    flyer.save(flyer_path)
    saved = Flyer.load(flyer_path)
    if {pos for pos, _ in saved.blocks()} != {(0, y, 0) for y in range(3)}:
        raise RuntimeError("saved driver fixture coordinates changed unexpectedly")

    for word, case in CASES.items():
        ticks = case["period"] * 3
        rows = []
        for cycle in range(3):
            moved_before = 0
            for offset, y in zip(case["ticks"], case["rows_y"]):
                target_x = cycle * case["advance"] + moved_before
                rows.append(f"{cycle * case['period'] + offset} {target_x} {y} 0 3")
                moved_before += 1
        script_path = scripts / f"{word}.txt"
        script_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        loads = [3 if char == "m" else None for char in word]
        spare = [0 if char == "m" else None for char in word]
        contract = {
            "version": 1,
            "name": f"external_drive_{word}",
            "flyer": "../driver.flyer",
            "drive_script": f"../drives/{word}.txt",
            "period_ticks": case["period"],
            "advance": case["advance"],
            "cycles": 3,
            "ports": [
                {"name": "driver_low", "role": "input", "at": [0, 0, 0],
                 "word": word, "baseline_load": loads, "spare_load": spare},
                {"name": "passenger", "role": "output", "at": [0, 1, 0],
                 "word": word},
                {"name": "driver_high", "role": "input", "at": [0, 2, 0],
                 "word": word, "baseline_load": loads, "spare_load": spare},
            ],
            "recurrence": "exact",
        }
        write_json(contracts / f"{word}.json", contract)
        print(f"built {word}: {len(rows)} scheduled ordinary piston drives, {ticks} ticks")

    # Negative controls for the external fixture boundary and source cap.
    budget_rows = []
    for cycle in range(3):
        for offset, y in zip(CASES["mmmww"]["ticks"], CASES["mmmww"]["rows_y"]):
            target_x = cycle * 3 + offset // 2
            budget_rows.append(f"{cycle * 10 + offset} {target_x} {y} 0 2")
    (scripts / "budget.txt").write_text("\n".join(budget_rows) + "\n", encoding="utf-8")
    negative_ports = [
        {"name": "driver_low", "role": "input", "at": [0, 0, 0],
         "word": "mmmww", "baseline_load": [3, 3, 3, None, None],
         "spare_load": [0, 0, 0, None, None]},
        {"name": "passenger", "role": "output", "at": [0, 1, 0], "word": "mmmww"},
        {"name": "driver_high", "role": "input", "at": [0, 2, 0],
         "word": "mmmww", "baseline_load": [3, 3, 3, None, None],
         "spare_load": [0, 0, 0, None, None]},
    ]
    write_json(
        contracts / "budget.json",
        {"version": 1, "name": "external_drive_budget_limit_2",
         "flyer": "../driver.flyer", "drive_script": "../drives/budget.txt",
         "period_ticks": 10, "advance": 3, "cycles": 3,
         "ports": negative_ports, "recurrence": "exact"},
    )

    collision = Flyer(rng_state=5, phase_x=0, phase_z=0, push_limit=12)
    collision.set((0, 0, 0), Block(Kind.REDSTONE_BLOCK))
    for y in range(3):
        collision.set((2, y, 0), Block(Kind.SLIME))
    collision_path = HERE / "collision.flyer"
    collision.save(collision_path)
    collision_rows = [f"{tick} {2 + cycle * 3} 0 0 3"
                      for cycle in range(3) for tick in (cycle * 10,)]
    (scripts / "collision.txt").write_text("\n".join(collision_rows) + "\n", encoding="utf-8")
    write_json(
        contracts / "collision.json",
        {"version": 1, "name": "external_drive_fixture_collision",
         "flyer": "../collision.flyer", "drive_script": "../drives/collision.txt",
         "period_ticks": 10, "advance": 3, "cycles": 3,
         "ports": [
             {"name": "driver_low", "role": "input", "at": [2, 0, 0],
              "word": "mmmww", "baseline_load": [3, 3, 3, None, None],
              "spare_load": [0, 0, 0, None, None]},
             {"name": "passenger", "role": "output", "at": [2, 1, 0],
              "word": "mmmww"},
             {"name": "driver_high", "role": "input", "at": [2, 2, 0],
              "word": "mmmww", "baseline_load": [3, 3, 3, None, None],
              "spare_load": [0, 0, 0, None, None]},
         ], "recurrence": "exact"},
    )


if __name__ == "__main__":
    main()
