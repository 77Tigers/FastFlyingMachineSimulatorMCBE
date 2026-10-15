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
    ap.add_argument("--rider-fires", default="", help="comma list of fire slots; each adds a lone-piston rider whose "
                    "word is every slot except f, f+1 (it is carried by the moving bodies the rest of the time)")
    a = ap.parse_args()
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
                     riders=riders, names=names)
    except Infeasible as e:
        print("trivially infeasible:", e)
        return 1
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
