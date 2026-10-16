"""Bodies from pistons, globally: design a whole flyer for given movement words with the exact CP-SAT model
(two_bps_20261007/satflyer5.py, any slot count), then verify it with contract-solve (80 samples).

usage: python design_sat.py OUT_DIR --words mmww,wwmm [--L 10] [--box m2:3,m1:2,m1:2] [--tl 60] [--workers 8]
       python design_sat.py OUT_DIR --problem PROBLEM.json [...]    (words taken from the contract's ports)
Offline tool (seconds to minutes), not part of the 5 s solver. Writes OUT_DIR/design.flyer, design.json (natural
contract, ports = one glue cell per segment) and the contract-solve report of the verification.
"""
import argparse, itertools, json, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "two_bps_20261007"))
sys.path.insert(0, str(ROOT))
from satflyer5 import FlyerSAT, to_flyer, show, Infeasible  # noqa: E402
from fastflyer import Flyer  # noqa: E402

SOLVER = ROOT / "target" / "release" / ("contract-solve.exe" if sys.platform == "win32" else "contract-solve")


def rng(s):
    a, b = (int(z) for z in s.replace("m", "-").split(":"))
    return range(a, b + 1)


def chain_spec(back: str, length: int):
    """Chain / tentacle (as in human_3bps_original): body i's LAST move is a pull by a sticky on body i+1 (the body
    in front), so body i+1 must be still in that slot and the one before. Each body's word is the back word shifted
    by the smallest offset that allows this; the tip is only pushed. Pushes whose slot has no carrier that is still
    in that slot and the next get a rider (a lone pusher carried by the bodies). Returns (words, force, rider fires)."""
    n = len(back)
    mv = [i for i, c in enumerate(back) if c == "m"]
    # moves as one cyclic run: the last move is the slot just before the first wait after a move
    last0 = next(s for s in range(n) if back[s] == "m" and back[(s + 1) % n] == "w")
    rot = lambda w, d: "".join(w[(i + d) % n] for i in range(n))  # word moving d slots earlier
    words = [back]
    for _ in range(length - 1):
        prev = words[-1]
        last = next(s for s in range(n) if prev[s] == "m" and prev[(s + 1) % n] == "w")
        for d in range(1, n):
            cand = rot(prev, d)
            if cand[last] == "w" and cand[(last - 1) % n] == "w":
                words.append(cand)
                break
        else:
            raise SystemExit(f"chain: no offset lets body {len(words)} pull body {len(words) - 1}")
    force = []
    for i in range(length - 1):
        last = next(s for s in range(n) if words[i][s] == "m" and words[i][(s + 1) % n] == "w")
        force.append(f"{i}:{last}:S:{i + 1}")
    fires = []
    for i, w in enumerate(words):
        last = next(s for s in range(n) if w[s] == "m" and w[(s + 1) % n] == "w")
        for s in range(n):
            if w[s] != "m" or (i < length - 1 and s == last):
                continue  # pulled moves are made by the front body's sticky
            if not any(j != i and words[j][s] == "w" and words[j][(s + 1) % n] == "w" for j in range(length)):
                fires.append(s)
    _ = (mv, last0)
    return words, ",".join(force), fires


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--words", default="")
    ap.add_argument("--problem", type=Path)
    ap.add_argument("--L", type=int, default=12)
    ap.add_argument("--box", default="m2:3,m1:2,m1:2")
    ap.add_argument("--tl", type=float, default=60)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--maxglue", type=int, default=6)
    ap.add_argument("--obj", default="maxload")
    ap.add_argument("--skip", default="", help="comma list of satflyer5 constraint groups to drop (diagnosis only: power, adh, move, conn, cause, targets)")
    ap.add_argument("--force", default="", help="comma list j:t:K:s = segment j's move at slot t is made by a piston "
                    "of kind K (P push / S sticky pull) on segment s (s = body index, or r<i> for rider i). Chains "
                    "(tentacles): each body's last move is a pull by a sticky on the body in front")
    ap.add_argument("--rider-fires", default="", help="comma list of fire slots; each adds a lone-piston rider whose "
                    "word is every slot except f, f+1 (it is carried by the moving bodies the rest of the time)")
    ap.add_argument("--chain", type=int, default=0, help="chain (tentacle) of this many bodies from the FIRST word "
                    "(the back body): words, pulls and riders are derived (see chain_spec)")
    a = ap.parse_args()
    if a.chain:
        w, force, fires = chain_spec(a.words.split(",")[0], a.chain)
        a.words, a.force, a.rider_fires = ",".join(w), ",".join(x for x in [force, a.force] if x), ",".join(str(x) for x in fires)
        print(f"chain: words {a.words}  pulls {force}  rider fire slots {a.rider_fires or '-'}")
    if a.problem:
        c = json.loads(a.problem.read_text())
        words_s = [p["word"] for p in c["ports"]]
    else:
        words_s = a.words.split(",")
    NS = len(words_s[0])
    words = [tuple(i for i, ch in enumerate(w) if ch == "m") for w in words_s]
    nb = len(words)
    for f in (int(x) for x in a.rider_fires.split(",") if x):
        words.append(tuple(s for s in range(NS) if s not in (f % NS, (f + 1) % NS)))
    riders = list(range(nb, len(words)))
    names = [f"s{i}" for i in range(nb)] + [f"r{i}" for i in range(len(riders))]
    box = list(itertools.product(*[rng(r) for r in a.box.split(",")]))
    kinds = ["g", "R"] + [f"D{q}" for q in range(6)] + [f"O{q}" for q in range(6)]
    t = time.time()
    try:
        S = FlyerSAT(words, box, a.L, NS=NS, kinds=kinds, leaf=True, maxglue=a.maxglue, anchor=(0, 0, 0),
                     riders=riders, names=names, skip=tuple(x for x in a.skip.split(",") if x))
    except Infeasible as e:
        print("trivially infeasible:", e)
        return 1
    for f in (x for x in a.force.split(",") if x):
        j, ts, kind, s = f.split(":")
        j, ts = int(j), int(ts)
        s = nb + int(s[1:]) if s.startswith("r") else int(s)
        lits = [l for (l, seg, k) in S.cause_lits.get((j, ts), []) if seg == s and k[0] == kind]
        if not lits:
            print(f"force {f}: no candidate piston in the model (check words / box)")
            return 1
        S.m.Add(sum(lits) == 1)
    st, dt = S.solve(a.tl, a.workers, objective=(None if a.obj == "none" else a.obj))
    print(f"CP-SAT {st} in {time.time() - t:.1f}s (words {words_s}, NS {NS}, L {a.L}, box {a.box})")
    if st not in ("OPTIMAL", "FEASIBLE"):
        return 1
    sol = S.extract()
    ml = max(S.loads().values())
    print(show(sol))
    print("causes:", " ".join(f"{t}:{a}<-{k}({b})" for t, a, k, b, _ in S.causes()))
    a.out.mkdir(parents=True, exist_ok=True)
    f = to_flyer(sol, max(ml, 1), NS)
    f.save(a.out / "design.flyer")
    # natural contract: one glue cell per segment as its port (coordinates after save normalisation)
    g = Flyer.load(a.out / "design.flyer")
    cells0 = [c for _, _, cells, _ in sol for c in cells]
    mn = lambda v: tuple(min(p[i] for p in v) for i in range(3))
    sa, sb = mn(cells0), mn([tuple(p) for p in g._cells])
    d = tuple(sb[i] - sa[i] for i in range(3))
    ports = []
    for i, (nm, w, cells, mat) in enumerate(sol):
        glue = sorted(c for c, k in cells.items() if k == "g")
        if not glue:
            continue
        at = [glue[0][0] + d[0], glue[0][1] + d[1], glue[0][2] + d[2]]
        ports.append({"name": nm, "role": "output", "at": at, "word": "".join("m" if s in w else "w" for s in range(NS))})
    adv = len(words[0])
    contract = {"version": 1, "name": f"design_{'_'.join(words_s)}", "flyer": "design.flyer", "period_ticks": 2 * NS,
                "advance": adv, "cycles": 3, "recurrence": "advance", "ports": ports}
    (a.out / "design.json").write_text(json.dumps(contract, indent=1) + "\n")
    r = subprocess.run([str(SOLVER), str(a.out / "design.json"), str(a.out / "verify"), "--budget", "5", "--quiet"],
                       capture_output=True, text=True, cwd=ROOT)
    print("contract-solve:", r.stdout.strip()[:200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
