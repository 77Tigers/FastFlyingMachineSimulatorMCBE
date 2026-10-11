"""Hand-designed observerless flyers (no search). Each design is a readable block table.

usage: python build.py NAME [PL] [--trace N]   -> writes runs/NAME_L<PL>.flyer, measures 10000 ticks
"""
from __future__ import annotations
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Block, Flyer, Kind  # noqa: E402

HERE = Path(__file__).resolve().parent
TOOL = ROOT / "target" / "release" / "fastflyer-research.exe"
PX, NX, PY, NY, PZ, NZ = range(6)  # +x -x +y -y +z -z

def piston(d, sticky=False): return Block.piston(direction=d, sticky=sticky)
def rod(d): return Block.rod(direction=d)
SLIME, HONEY, GLASS, STONE, RB, TERRA = (Block(Kind.SLIME), Block(Kind.HONEY), Block(Kind.GLASS),
                                         Block(Kind.SMOOTH_STONE), Block(Kind.REDSTONE_BLOCK),
                                         Block(Kind.GLAZED_TERRACOTTA))

DESIGNS: dict[str, dict] = {
    # shuttle11: compact push/pull engine; observers replaced by a rod shuttle D and a redstone block.
    # A (rear, honey glue): P0 pushes D+B, sticky so its retraction pulls the rod D back alone.
    # B (front, slime glue): pushed by D; P1 pulls A. D faces +z: at tick 2 (D forward) it hard-powers
    # honey X, which powers P1; at ticks 0 and 4 D faces glass (not solid). RB powers P0 only while
    # A and B touch (near). Every same-tick pair of actions is order independent.
    "shuttle11": {
        (0, 0, 0): piston(PX, sticky=True),  # P0 (A)
        (0, 0, 1): HONEY,                    # A glue P0-H
        (0, 1, 1): HONEY,                    # H, pulled by P1
        (1, 0, 1): GLASS,                    # A, pushes X along; D's target at ticks 0 and 4
        (2, 0, 1): HONEY,                    # X, D's target at tick 2 -> powers P1
        (1, 0, 0): rod(PZ),                  # D shuttle
        (2, 0, 0): SLIME,                    # E (B), pushed by D
        (2, 1, 0): SLIME,                    # B glue
        (1, 1, 0): SLIME,                    # B glue
        (1, 1, 1): piston(NX, sticky=True),  # P1 (B)
        (0, 1, 0): RB,                       # powers P0 while near
    },
}

def build(name: str, pl: int) -> Path:
    f = Flyer(push_limit=pl)
    for pos, block in DESIGNS[name].items():
        f.set(pos, block)
    out = HERE / "runs" / f"{name}_L{pl}.flyer"
    f.save(out)
    return out

def run(*args) -> str:
    r = subprocess.run([str(TOOL), *map(str, args)], capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()

if __name__ == "__main__":
    name = sys.argv[1]
    pl = int(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else 12
    path = build(name, pl)
    kinds = {}
    for _, b in DESIGNS[name].items():
        kinds[b.kind.name] = kinds.get(b.kind.name, 0) + 1
    print(name, "blocks", len(DESIGNS[name]), kinds, "PL", pl)
    print(run("measure", path, 10000))
    if "--trace" in sys.argv:
        n = int(sys.argv[sys.argv.index("--trace") + 1])
        print(run("trace", path, 0, n))
