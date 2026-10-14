import json, subprocess, sys, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pieceA as A
import xlib as X
from pieceA import *

def verify(dirp, riders, order="before_natural", samples=((0,0,0),(1,7,8),(42,15,15),(5,8,7))):
    """riders: {body: pos}. Checks the rider's moves equal its body's word every cycle and that it never acts."""
    out = {}
    for sample in samples:
        c, rows = X.fixture_trace(dirp, order, "bounded", sample, 30)
        pos2id = {tuple(cc[:3]): tuple(cc[:3]) for cc in rows[0]["trace"]["initial"] if (cc[3] & 15) != 10}
        moves = {b: [] for b in riders}; acted = {b: 0 for b in riders}
        for r in rows:
            for s in r["trace"]["steps"]:
                mv = s.get("movement")
                ap = s.get("active_piston")
                if s["action"] in ("extend", "retract") and ap is not None:
                    for b, q in riders.items():
                        if pos2id.get(tuple(ap)) == q: acted[b] += 1
                if mv and mv.get("sources") and mv.get("destinations"):
                    m = {tuple(x): tuple(y) for x, y in zip(mv["sources"], mv["destinations"])}
                    idm = [(pos2id[x], x, y) for x, y in m.items() if x in pos2id]
                    for i, x, y in idm:
                        for b, q in riders.items():
                            if i == q: moves[b].append(r["tick"])
                    for i, x, y in idm: pos2id.pop(x)
                    for i, x, y in idm: pos2id[y] = i
        for b in riders:
            out.setdefault(b, []).append((acted[b], sorted(set(t % 10 // 2 for t in moves[b])), len(moves[b])))
    return out

if __name__ == "__main__":
    single = json.load(open(HERE / "A_single.json"))
    words = {p["body"]: p["word"] for p in plan["ports"]}
    good = {}
    for b, lst in single.items():
        good[b] = []
        for q, po in lst:
            q = tuple(q)
            d = HERE / "A_work" / f"{b}_{q[0]}_{q[1]}_{q[2]}"
            v = verify(d, {b: q})[b]
            wslots = [i for i, ch in enumerate(words[b]) if ch == "m"]
            ok = all(a == 0 and s == wslots and n == 9 for a, s, n in v)
            if ok: good[b].append(q)
        print(b, words[b], len(single[b]), "->", len(good[b]), "carried on all 3 moves, never acts:", good[b][:8])
    json.dump({b: [list(q) for q in v] for b, v in good.items()}, open(HERE / "A_good.json", "w"))
