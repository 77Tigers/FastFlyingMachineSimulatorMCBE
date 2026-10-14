"""(c) 7-cell back bodies: delete one cell (or move a neighbouring non-glue cell into the hole) of one back body of core0 and evaluate."""
import sys, json, shutil, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "extract"))
import xlib as X
from xlib import Flyer, Block, Kind
SRC = HERE / "core0_np"
nm = {tuple(json.loads(k.replace('(', '[').replace(')', ']'))): v for k, v in json.load(open(HERE / "core0_names.json")).items()}
D6 = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
BACK = ['B7', 'B8', 'B9', 'B15', 'B16']
base = Flyer.load(SRC / "candidate.flyer")
c0 = {o: json.loads((SRC / f"bounded_{o}.json").read_text()) for o in X.ORDERS}

def make(out: Path, edits, cap=None):
    """edits: dict pos -> None (delete) or Block (set). Returns True if written."""
    out.mkdir(parents=True, exist_ok=True)
    f = Flyer(rng_state=base.rng_state, phase_x=base.phase_x, phase_z=base.phase_z, push_limit=base.push_limit)
    cells = {p: b for p, b in base.blocks()}
    for p, b in edits.items():
        if b is None: cells.pop(p, None)
        else: cells[p] = b
    for p, b in cells.items(): f.set(p, b)
    for p, b in base.blocks():
        if b.kind == Kind.PISTON and p in cells:
            ob = base.get_piston_blocks(p)
            if ob: f.set_piston_blocks(p, [q for q in ob if q in cells])
    f.save(out / "candidate.flyer")
    g = Flyer.load(out / "candidate.flyer")
    if {p: b.encode() for p, b in g.blocks()} != {p: b.encode() for p, b in f.blocks()}: return False
    shutil.copy(SRC / "drive.txt", out / "drive.txt")
    ids = [p for p, b in g.blocks() if b.kind != Kind.PISTON_ARM]
    env = {"min": [min(p[i] for p in ids) for i in range(3)], "max": [max(p[i] for p in ids) for i in range(3)]}
    for o in X.ORDERS:
        c = json.loads(json.dumps(c0[o]))
        c["boundary_envelope"] = env
        c["required_cells"] = [r for r in c["required_cells"] if tuple(r["at"]) not in edits]
        for p, b in edits.items():
            if b is not None and not any(tuple(r["at"]) == p for r in c["required_cells"]) and nm.get(p) and False: pass
        # ports on deleted/moved cells: move to another glue cell of the same body
        for pt in c["ports"]:
            at = tuple(pt["at"])
            if at in edits:
                body = nm[at][0]
                alt = sorted(q for q, (b, k) in nm.items() if b == body and k in ("sl", "ho") and q not in edits)
                pt["at"] = list(alt[0])
        if cap:
            for pt in c["ports"]:
                if "baseline_load" in pt: pt["baseline_load"] = [None if b is None else min(b, cap) for b in pt["baseline_load"]]
        (out / f"bounded_{o}.json").write_text(json.dumps(c, indent=2) + "\n")
    return True

def variants(body):
    cs = sorted(q for q, (b, k) in nm.items() if b == body)
    out = []
    for c in cs:
        out.append((f"del{c}", {c: None}))
        for d in D6:
            n = (c[0]+d[0], c[1]+d[1], c[2]+d[2])
            if n in nm and nm[n][0] == body and nm[n][1] != nm[c][1] and nm[n][1] not in ('P', 'S'):
                out.append((f"del{c}+move{n}", {c: base.get(n), n: None}))
    return out

def count12(out, order="before_natural", cyc=1, thr=12):
    sys.path.insert(0, str(HERE))
    from actions import actions
    a = actions(out, order, "bounded", (0,0,0), cyc)
    nat = [x for x in a if x[1] != 'prescribed move']
    return max(x[3] for x in nat), sum(1 for x in nat if x[3] >= thr), sorted((x[0], x[3]) for x in nat if x[3] >= thr)

if __name__ == "__main__":
    which = sys.argv[1:] or BACK
    for body in which:
        print("==", body, len([q for q, (b, k) in nm.items() if b == body]), "cells", flush=True)
        for name, ed in variants(body):
            out = HERE / "c_work" / f"{body}_{abs(hash(name)) % 10**8}"
            if not make(out, ed): print(name, "translated"); continue
            r = {o: X.evaluate(out, "bounded", o).get("pass") for o in ("before_natural", "after_natural", "interleaved")}
            if not r["before_natural"]:
                print(name, "FAIL-before", str(X.evaluate(out, 'bounded', 'before_natural').get('first_failure'))[-90:]); shutil.rmtree(out, ignore_errors=True); continue
            mx, n12, l12 = count12(out)
            print(name, "pass", [k[0] for k, v in r.items() if v], "max", mx, "n>=12:", n12, l12, flush=True)
            shutil.rmtree(out, ignore_errors=True)
