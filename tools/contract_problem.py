"""Turn a solved contract (e.g. an extension-bank entry) into an unsolved *problem* for contract-solve.

A problem is the same version-1 contract with its flyer reduced to the pinned cells (`required_cells`).
Saving a flyer renormalises coordinates (min Y = 0, chunk-aligned X/Z), so every absolute coordinate in
the contract and drive script is shifted to match the saved problem flyer.

usage: python tools/contract_problem.py CONTRACT.json OUT_DIR [--keep-hardware]
       python tools/contract_problem.py --bank-entry flyers/extension_bank/n3/n3_134 OUT_DIR
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer  # noqa: E402


def _min_corner(cells):
    xs = [p[0] for p in cells]
    ys = [p[1] for p in cells]
    zs = [p[2] for p in cells]
    return min(xs), min(ys), min(zs)


def shift_contract(contract: dict, d: tuple[int, int, int]) -> dict:
    def sh(a):
        return [a[0] + d[0], a[1] + d[1], a[2] + d[2]]
    c = json.loads(json.dumps(contract))
    for p in c.get("ports", []):
        p["at"] = sh(p["at"])
    for r in c.get("required_cells", []):
        r["at"] = sh(r["at"])
    env = c.get("boundary_envelope")
    if env:
        env["min"] = sh(env["min"])
        env["max"] = sh(env["max"])
    return c


def shift_script(text: str, d) -> str:
    out = []
    for line in text.splitlines():
        core = line.split("#")[0].split()
        if len(core) == 5:
            t, x, y, z, cap = map(int, core)
            out.append(f"{t} {x + d[0]} {y + d[1]} {z + d[2]} {cap}")
    return "\n".join(out) + "\n"


def make_problem(contract_path: Path, out_dir: Path, keep_hardware: bool = False) -> Path:
    contract = json.loads(contract_path.read_text())
    src_dir = contract_path.parent
    flyer = Flyer.load(src_dir / contract["flyer"])
    req = {tuple(r["at"]) for r in contract.get("required_cells", [])}
    if not req:
        raise ValueError("contract has no required_cells: nothing is pinned, so a problem would be empty")
    before = [tuple(p) for p in flyer._cells]
    if not keep_hardware:
        for p in list(flyer._cells):
            if tuple(p) not in req:
                flyer.remove(p)
    kept = [tuple(p) for p in flyer._cells]
    out_dir.mkdir(parents=True, exist_ok=True)
    fpath = out_dir / "problem.flyer"
    flyer.save(fpath)
    saved = [tuple(p) for p in Flyer.load(fpath)._cells]
    a, b = _min_corner(kept), _min_corner(saved)
    d = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    c = shift_contract(contract, d)
    c["flyer"] = "problem.flyer"
    script = contract.get("prescribed_script")
    if script:
        (out_dir / "drive.txt").write_text(shift_script((src_dir / script).read_text(), d))
        c["prescribed_script"] = "drive.txt"
    c["name"] = contract.get("name", "problem").replace("-before_natural", "").replace("-after_natural", "")
    (out_dir / "problem.json").write_text(json.dumps(c, indent=1) + "\n")
    meta = {"source_contract": str(contract_path), "removed_cells": len(before) - len(kept), "shift": d}
    (out_dir / "problem_meta.json").write_text(json.dumps(meta) + "\n")
    return out_dir / "problem.json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("contract", nargs="?", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--bank-entry", type=Path)
    ap.add_argument("--keep-hardware", action="store_true")
    a = ap.parse_args()
    path = a.contract or (a.bank_entry / "before_natural.json")
    print(make_problem(path, a.out_dir, a.keep_hardware))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
