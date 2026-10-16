"""Bodies -> flyer through one extension contract per body (offline orchestrator, not the 5 s solver).

usage: python assemble.py PROBLEM.json OUT_DIR [--budget 5] [--rounds 2]

PROBLEM is a natural contract whose flyer holds only the bodies (e.g. contract-from-flyer `bare`, or a CP-SAT
layout stripped to glue). For every body k an extension contract is written: body k's moves natural (output port),
every other body's moves prescribed (input ports, drive.txt), no hardware. contract-solve solves each; the hardware
found for all bodies is merged onto the bodies and the merged flyer is checked as the natural contract. If the
merge fails, round 2 re-solves each body's contract with the other bodies' hardware already present (unpinned),
then merges again. Why bodies, not moves: chains / pusher columns serve several moves of one body (see README).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer  # noqa: E402

SOLVER = ROOT / "target" / "release" / ("contract-solve.exe" if sys.platform == "win32" else "contract-solve")


def body_of(cells: dict, at: tuple) -> set:
    """glue component (same material) containing `at`"""
    k = cells[at].kind
    seen, st = {at}, [at]
    while st:
        p = st.pop()
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            q = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
            if q not in seen and q in cells and cells[q].kind == k:
                seen.add(q)
                st.append(q)
    return seen


def port_pos(port: dict, tick: int, period: int, adv: int) -> tuple:
    w = port["word"]
    slot = (tick % period) // 2
    pre = sum(1 for c in w[:slot] if c == "m")
    return (port["at"][0] + (tick // period) * adv + pre, port["at"][1], port["at"][2])


def ext_contract(c: dict, k: int, cap: int, out: Path, flyer_src: Path, extra: dict | None):
    """contract for body k (ports of body k natural, the rest prescribed); extra = hardware cells to add."""
    out.mkdir(parents=True, exist_ok=True)
    f = Flyer.load(flyer_src)
    for p, b in (extra or {}).items():
        f.set(p, b)
    f.save(out / "problem.flyer")
    # saving renormalises coordinates: shift everything by the same delta as the pinned cells
    g = Flyer.load(out / "problem.flyer")
    a0 = min(tuple(p) for p in Flyer.load(flyer_src)._cells)
    src_min = tuple(min(p[i] for p in list(Flyer.load(flyer_src)._cells) + list((extra or {}).keys())) for i in range(3))
    dst_min = tuple(min(p[i] for p in g._cells) for i in range(3))
    d = tuple(dst_min[i] - src_min[i] for i in range(3))
    _ = a0
    sh = lambda p: [p[0] + d[0], p[1] + d[1], p[2] + d[2]]
    period, adv, cycles = c["period_ticks"], c["advance"], c.get("cycles", 3)
    cells = {tuple(p): b for p, b in Flyer.load(flyer_src)._cells.items()}
    kbody = set()
    for kk in (k if isinstance(k, (list, tuple, set)) else [k]):
        kbody |= body_of(cells, tuple(c["ports"][kk]["at"]))
    ports, rows = [], []
    for j, p in enumerate(c["ports"]):
        mine = tuple(p["at"]) in kbody
        q = dict(p)
        q["at"] = sh(p["at"])
        q["role"] = "output" if mine else "input"
        ports.append(q)
        if mine:
            continue
        for cyc in range(cycles):
            for s, ch in enumerate(p["word"]):
                if ch == "m":
                    t = cyc * period + 2 * s
                    x, y, z = port_pos(p, t, period, adv)
                    rows.append((t, x + d[0], y + d[1], z + d[2]))
    # one stroke per port and tick (bare problems have one port per body)
    seen, lines = set(), []
    for t, x, y, z in sorted(rows):
        if (t, x, y, z) in seen:
            continue
        seen.add((t, x, y, z))
        lines.append(f"{t} {x} {y} {z} {cap}")
    (out / "drive.txt").write_text("\n".join(lines) + "\n")
    req = [{"at": sh(r["at"]), "cell": r["cell"]} for r in c["required_cells"]]
    e = {"version": 1, "name": f"{c.get('name', 'problem')}-bodies", "flyer": "problem.flyer", "prescribed_script": "drive.txt",
         "prescribed_order": "before_natural", "period_ticks": period, "advance": adv, "cycles": cycles,
         "recurrence": c.get("recurrence", "advance"), "ports": ports, "required_cells": req}
    if not lines:  # every body natural: a plain natural contract
        e.pop("prescribed_script")
        e.pop("prescribed_order")
        (out / "drive.txt").unlink()
    if c.get("boundary_envelope"):
        e["boundary_envelope"] = {"min": sh(c["boundary_envelope"]["min"]), "max": sh(c["boundary_envelope"]["max"])}
    (out / "problem.json").write_text(json.dumps(e, indent=1) + "\n")
    return d


def solve(prob: Path, out: Path, budget: float, seed: int = 1) -> dict:
    subprocess.run([str(SOLVER), str(prob), str(out), "--budget", str(budget), "--quiet", "--holdout", "--seed", str(seed)], capture_output=True, cwd=ROOT)
    try:
        return json.loads((out / "report.json").read_text())
    except Exception:
        return {"status": "crash"}


def hardware(sol_flyer: Path, pinned: set, d: tuple) -> dict:
    """non-pinned cells of a solution, mapped back to the problem frame (minus the shift d)"""
    f = Flyer.load(sol_flyer)
    cells = {tuple(p): b for p, b in f._cells.items()}
    # the solution was saved again (renormalised): align by the pinned cells
    from collections import Counter
    pin = {tuple(p) for p in pinned}
    votes = Counter((p[0] - q[0], p[1] - q[1], p[2] - q[2]) for q in cells for p in pin if True)
    best = None
    for (dx, dy, dz), _ in votes.most_common(30):
        hit = sum(1 for q in cells if (q[0] + dx, q[1] + dy, q[2] + dz) in pin)
        if best is None or hit > best[0]:
            best = (hit, (dx, dy, dz))
    dx, dy, dz = best[1]
    return {(q[0] + dx, q[1] + dy, q[2] + dz): b for q, b in cells.items() if (q[0] + dx, q[1] + dy, q[2] + dz) not in pin}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("problem", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--budget", type=float, default=5)
    ap.add_argument("--rounds", type=int, default=2)
    a = ap.parse_args()
    c = json.loads(a.problem.read_text())
    src = a.problem.parent / c["flyer"]
    pinned = {tuple(r["at"]) for r in c["required_cells"]}
    cells0 = {tuple(p): b for p, b in Flyer.load(src)._cells.items()}
    bodies, ports_of = [], []
    for j, p in enumerate(c["ports"]):
        b = body_of(cells0, tuple(p["at"]))
        if b not in bodies:
            bodies.append(b)
            ports_of.append(j)
    cap = 64

    def merged_check(tag: str, hw: dict) -> dict:
        """the bodies + hardware as the natural contract (contract-solve's seed stage checks it, search may repair)"""
        mdir = a.out / tag
        mdir.mkdir(parents=True, exist_ok=True)
        f = Flyer.load(src)
        for p, b in hw.items():
            f.set(p, b)
        f.save(mdir / "merged.flyer")
        g = Flyer.load(mdir / "merged.flyer")
        smin = tuple(min(p[i] for p in list(cells0) + list(hw)) for i in range(3))
        dmin = tuple(min(p[i] for p in g._cells) for i in range(3))
        dd = tuple(dmin[i] - smin[i] for i in range(3))
        cm = json.loads(json.dumps(c))
        cm["flyer"] = "merged.flyer"
        for p in cm["ports"]:
            p["at"] = [p["at"][i] + dd[i] for i in range(3)]
        for r_ in cm["required_cells"]:
            r_["at"] = [r_["at"][i] + dd[i] for i in range(3)]
        if cm.get("boundary_envelope"):
            for kk in ("min", "max"):
                cm["boundary_envelope"][kk] = [cm["boundary_envelope"][kk][i] + dd[i] for i in range(3)]
        (mdir / "problem.json").write_text(json.dumps(cm, indent=1) + "\n")
        r = solve(mdir / "problem.json", mdir / "sol", a.budget)
        print(f"{tag} ({len(hw)} hardware cells): {r.get('status')} load={r.get('endogenous_max_load')} src={str(r.get('source'))[:60]}", flush=True)
        return r

    # round 1: every body alone (others prescribed), then merge
    own: dict = {}
    merged: dict = {}
    for bi, j in enumerate(ports_of):
        d = ext_contract(c, j, cap, a.out / f"r1_body{bi}", src, None)
        r = solve(a.out / f"r1_body{bi}" / "problem.json", a.out / f"r1_body{bi}" / "sol", a.budget)
        print(f"round 1 body {bi} ({len(bodies[bi])} cells): {r.get('status')} load={r.get('endogenous_max_load')}", flush=True)
        if r.get("status") in ("verified", "unverified_pass"):
            own[bi] = hardware(a.out / f"r1_body{bi}" / "sol" / "solution.flyer", pinned, d)
            for p, b in own[bi].items():
                merged.setdefault(p, b)
    if merged_check("r1_merged", merged).get("status") == "verified":
        return 0
    if a.rounds < 2:
        return 1
    # round 2: sequential, bodies added one at a time: the bodies solved so far are natural with their hardware
    # present (unpinned, the solver may change it); the new body's own round-1 hardware is added as a hint
    hw: dict = {}
    natural: list = []
    # passes over the bodies still missing (later bodies change the context of earlier failures)
    for pas in range(3):
        before = len(natural)
        for bi, j in enumerate(ports_of):
            if bi in natural:
                continue
            extra = dict(hw)
            for p, b in own.get(bi, {}).items():
                extra.setdefault(p, b)
            tag = f"r2_p{pas}_step{bi}"
            d = ext_contract(c, [ports_of[x] for x in natural] + [j], cap, a.out / tag, src, extra)
            # a few solver seeds per step: the greedy sequence is sensitive to which solution a step returns
            for seed in (1, 2, 3):
                r = solve(a.out / tag / "problem.json", a.out / tag / "sol", a.budget, seed)
                ok = r.get("status") in ("verified", "unverified_pass")
                if ok:
                    break
            print(f"round 2 pass {pas} +body {bi}: {len(natural) + 1} bodies natural -> {r.get('status')} load={r.get('endogenous_max_load')}", flush=True)
            if ok:
                hw = hardware(a.out / tag / "sol" / "solution.flyer", pinned, d)
                natural.append(bi)
        if len(natural) == len(ports_of) or len(natural) == before:
            break
    if len(natural) == len(ports_of):
        return 0 if merged_check("r2_merged", hw).get("status") == "verified" else 1
    print(f"round 2: {len(natural)}/{len(ports_of)} bodies natural; missing {sorted(set(range(len(ports_of))) - set(natural))}")
    return 1

hw_owner: dict = {}

if __name__ == "__main__":
    raise SystemExit(main())
