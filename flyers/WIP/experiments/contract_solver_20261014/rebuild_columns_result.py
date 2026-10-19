"""Rebuild the validated reconstruction from its tracked encoded-cell artifact."""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from fastflyer import Block, Flyer


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("output", type=Path)
    ap.add_argument("--artifact", type=Path, default=HERE / "results/columns_reconstruction.json")
    a = ap.parse_args()
    data = json.loads(a.artifact.read_text())
    flyer = Flyer(**data["flyer_parameters"])
    for x, y, z, value in data["cells"]:
        flyer.set((x, y, z), Block.decode(value))
    for owner in data["piston_owners"]:
        flyer.set_piston_blocks(tuple(owner["at"]), map(tuple, owner["blocks"]))
    if flyer.content_hash() != data["content_hash"]:
        raise RuntimeError("encoded artifact content hash does not match")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    flyer.save(a.output)
    loaded = Flyer.load(a.output)
    if loaded.content_hash() != data["content_hash"]:
        raise RuntimeError("saved reconstruction content hash does not match")
    print(f"Rebuilt {len(data['cells'])} cells at PL{flyer.push_limit}: {a.output}")


if __name__ == "__main__":
    main()
