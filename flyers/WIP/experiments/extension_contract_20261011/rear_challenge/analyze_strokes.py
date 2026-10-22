"""Extract actual actions carrying the tagged K0 identity from a Rust trace."""

from __future__ import annotations
import os as _research_os

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from fastflyer import Block, Flyer, Kind

FLYER = ROOT / "flyers/bank/pl7/tm_7pl_2.5bps.flyer"
TRACE = ROOT / ('target/release/extension-trace' + ('.exe' if _research_os.name == 'nt' else ''))
PORT_ORIGIN = (0, 1, 15)


def main() -> None:
    process = subprocess.Popen(
        [str(TRACE), str(FLYER), "8", "5", "0", "0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    flyer = Flyer.load(FLYER)
    ids = {pos: pos for pos, block in flyer._cells.items() if block.kind != Kind.PISTON_ARM}
    port_id = PORT_ORIGIN
    world = {pos: block.encode() for pos, block in flyer._cells.items()}
    strokes = []
    assert process.stdout is not None
    for expected_tick, line in enumerate(process.stdout):
        trace = json.loads(line)
        assert trace["steps"]
        assert {tuple(row[:3]): row[3] for row in trace["initial"]} == world
        for step in trace["steps"]:
            movement = step.get("movement")
            if movement and movement.get("failure") is None:
                sources = [tuple(p) for p in movement["sources"]]
                destinations = [tuple(p) for p in movement["destinations"]]
                mapping = dict(zip(sources, destinations))
                moving_port = next((identity for identity, pos in ids.items()
                                    if identity == port_id and pos in mapping), None)
                if moving_port is not None:
                    slot = expected_tick // 2
                    source_rows = [
                        {"identity_origin": list(identity), "at": list(pos),
                         "kind": Block.decode(world[pos]).kind.name.lower()}
                        for identity, pos in ids.items() if pos in mapping
                    ]
                    strokes.append({
                        "tick": expected_tick,
                        "slot": slot,
                        "actor": step["active_piston"],
                        "action": step["action"],
                        "port_identity_origin": list(port_id),
                        "sources": source_rows,
                        "source_count": len(sources),
                    })
                ids = {identity: mapping.get(pos, pos) for identity, pos in ids.items()}
            for change in step["changes"]:
                pos = tuple(change[:3])
                if change[3] is None:
                    world.pop(pos, None)
                else:
                    world[pos] = change[3]
    process.stdout.close()
    stderr = process.stderr.read() if process.stderr else ""
    status = process.wait()
    if status:
        raise RuntimeError(f"extension-trace failed ({status}): {stderr}")
    result = {
        "source": "bank/pl7/tm_7pl_2.5bps.flyer",
        "rng": 5,
        "phase_x": 0,
        "phase_z": 0,
        "port": {"name": "rear_k0_input", "identity_at_load": list(PORT_ORIGIN), "word": "mmww"},
        "strokes": strokes,
    }
    out = Path(__file__).with_name("stroke_sources.json")
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"saved {len(strokes)} tagged strokes to {out}")


if __name__ == "__main__":
    main()
