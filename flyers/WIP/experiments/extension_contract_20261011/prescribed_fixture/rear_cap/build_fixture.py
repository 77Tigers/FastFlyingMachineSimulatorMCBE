"""Extract the PL7 K0/N/K1 start cap with its original identities and states."""
from __future__ import annotations

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Kind

REFERENCE = ROOT / "flyers/bank/pl7/tm_7pl_2.5bps.flyer"
KEEP = {
    # K0, five original identities.
    (0, 0, 15), (0, 1, 15), (0, 0, 16), (0, 1, 16), (0, 1, 17),
    # N identity and its original sticky actuator/arm.
    (2, 0, 15), (2, 1, 15), (1, 1, 15),
    # K1, six original identities.
    (2, 0, 17), (3, 0, 16), (3, 0, 17),
    (3, 1, 16), (3, 1, 17), (3, 2, 17),
    # K1 redstone input cell; prescribe its actual phase separately.
    (3, 2, 16),
}


def main() -> None:
    source = Flyer.load(REFERENCE)
    expected = {pos: block for pos, block in source.blocks() if pos in KEEP}
    if set(expected) != KEEP:
        raise RuntimeError(f"reference cells missing: {sorted(KEEP - set(expected))}")
    candidate = Flyer(rng_state=source.rng_state, phase_x=source.phase_x,
                      phase_z=source.phase_z, push_limit=source.push_limit)
    for pos, block in expected.items():
        candidate.set(pos, block)
    out = HERE / "candidate.flyer"
    candidate.save(out)
    saved = Flyer.load(out)
    actual = {pos: block for pos, block in saved.blocks()}
    if {pos: block.encode() for pos, block in actual.items()} != {
            pos: block.encode() for pos, block in expected.items()}:
        raise RuntimeError("save/load changed the selected initial block identities or states")
    rows = []
    for pos, block in sorted(actual.items()):
        rows.append({"at": list(pos), "encoded": block.encode(),
                     "kind": block.kind.name.lower(), "direction": block.direction,
                     "state": block.state, "sticky": block.sticky,
                     "powered": block.powered, "moving": block.moving})
    (HERE / "initial_blocks.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(f"saved {len(rows)} original K0/N/K1 cells including N sticky; push_limit={saved.push_limit}")


if __name__ == "__main__":
    main()
