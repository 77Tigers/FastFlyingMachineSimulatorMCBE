"""Generate minimal prescribed-input primitive calibration fixtures."""
from __future__ import annotations
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Block, Flyer, Kind

CASES = {
    "mmmww": {"period": 10, "advance": 3, "offsets": [0, 2, 4]},
    "mmmmww": {"period": 12, "advance": 4, "offsets": [0, 2, 4, 6]},
    "mmwmmw": {"period": 12, "advance": 4, "offsets": [0, 2, 6, 8]},
    "mmwwm": {"period": 10, "advance": 3, "offsets": [0, 2, 8]},
}

def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

def main() -> None:
    (HERE / "contracts").mkdir(exist_ok=True)
    (HERE / "scripts").mkdir(exist_ok=True)
    flyer = Flyer(rng_state=5, phase_x=0, phase_z=0, push_limit=3)
    for y in range(3):
        flyer.set((0, y, 0), Block(Kind.SLIME))
    flyer.save(HERE / "driver.flyer")
    saved = Flyer.load(HERE / "driver.flyer")
    if {p for p, _ in saved.blocks()} != {(0, y, 0) for y in range(3)}:
        raise RuntimeError("saved three-glue column changed")
    for word, case in CASES.items():
        period, advance = case["period"], case["advance"]
        rows = []
        for cycle in range(3):
            moved_before = 0
            for offset in case["offsets"]:
                rows.append(f"{cycle * period + offset} {cycle * advance + moved_before} 0 0 3")
                moved_before += 1
        script = HERE / "scripts" / f"{word}.txt"
        script.write_text("\n".join(rows) + "\n", encoding="utf-8")
        loads = [3 if ch == "m" else None for ch in word]
        spare = [0 if ch == "m" else None for ch in word]
        for order in ("before_natural", "after_natural"):
            contract = {
                "version": 1,
                "name": f"prescribed_primitive_{word}_{order}",
                "flyer": "../driver.flyer",
                "prescribed_script": f"../scripts/{word}.txt",
                "prescribed_order": order,
                "period_ticks": period,
                "advance": advance,
                "cycles": 3,
                "ports": [
                    {"name": "driver", "role": "input", "at": [0, 0, 0],
                     "word": word, "baseline_load": loads, "spare_load": spare},
                    {"name": "passenger", "role": "output", "at": [0, 1, 0], "word": word},
                ],
                "recurrence": "exact",
            }
            write_json(HERE / "contracts" / f"{word}_{order.removesuffix('_natural')}.json", contract)
        print(f"built {word}: {len(rows)} actions, {period * 3} ticks")
    (HERE / "scripts" / "negative_overbudget.txt").write_text("0 0 0 0 2\n", encoding="utf-8")
    (HERE / "scripts" / "negative_duplicate_moving_input.txt").write_text("0 0 0 0 3\n0 0 0 0 3\n", encoding="utf-8")

if __name__ == "__main__":
    main()


