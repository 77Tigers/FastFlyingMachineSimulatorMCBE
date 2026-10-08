"""Real-simulator fixture for POWER RIDERS (2026-10-07): a single redstone block / rod / observer W with no glue that
hops between carriers, like the hand-off piston V, and powers a piston on the way.

Every case is a tiny rig run for a few ticks with many RNG seeds and X/Z chunk phases (0,7,8,15)^2; the final state
must be the SAME for every seed/phase and equal the expected one. Cases (W kind in R, D (rod), O (observer)):
  A  glue hand-off: P1 pushes C1 (slime) at tick 0, C1's slime touches W -> W +1. W now powers P2 (R/D: adjacency,
     O: its movement pulse, facing P2). P2 fires at tick 2 and pushes C2 (honey) whose honey touches W -> W +1 again
     (W powers the very piston whose push carries it away: cached power).  C1 is idle then and still touches W.
  B  obstruction hand-off: same, but C1 carries W by a block right BEHIND W, C2 by a block right behind W.
  C  leaf race: as A, plus a co-moving segment J (own piston, same tick 0) whose glue also touches W.
  D  leaf PUSH race: as A, plus J moves INTO W's cell in tick 0 (W's destination is free).
  E  power cached while ANOTHER piston carries W away in the same tick: W powers P2 (fires tick 2) while P3 pushes
     C3 (glue touching W) at tick 2 too; random order. P2 must still fire, W must go with C3.
  F  NEGATIVE control (the hazard): W must stay, but an idle segment's glue that touches W moves -> W is dragged.
  G  observer pulse timing: W (observer) carried at tick 0, faces P2 -> P2 fires at tick 2 (not 0, not 4).
usage: python fixture.py [NSEEDS]   -> prints one line per case/kind; writes runs/fixture.txt
"""
import subprocess, sys, tempfile, pathlib
from collections import Counter
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Block, Kind
EXE = ROOT / 'target' / 'release' / ('fastflyer-sim.exe' if sys.platform == 'win32' else 'fastflyer-sim')
PHASES = (0, 7, 8, 15)


def wblock(kind, face=2):
    return {'R': Block(Kind.REDSTONE_BLOCK), 'D': Block.rod(face), 'O': Block.observer(face)}[kind]


def P(d=0, sticky=False): return Block.piston(d, sticky=sticky)


def S(): return Block(Kind.SLIME)
def H(): return Block(Kind.HONEY)
def RB(): return Block(Kind.REDSTONE_BLOCK)


def case_A(f, k):
    f.set((-1, 0, 0), RB()); f.set((0, 0, 0), P())           # P1 fires tick 0
    f.set((1, 0, 0), S()); f.set((2, 0, 0), S())              # C1
    f.set((2, 0, 1), wblock(k, 2))                            # W touches C1's slime (2,0,0)
    f.set((3, 1, 1), P())                                     # P2 (W lands at (3,0,1) below it)
    f.set((4, 1, 1), H()); f.set((4, 0, 1), H())              # C2: honey (4,0,1) right in front of W's landing cell
    return {'W': (4, 0, 1), 'ticks': 4}


def case_B(f, k):
    """obstruction carry on hop 1: C1 = slime + observer leaf (faces -Y, harmless) right BEHIND W (no glue contact);
    hop 2 by glue contact of C2's honey right in front of W (P2 above W's landing cell, powered by W)."""
    f.set((-1, 0, 0), RB()); f.set((0, 0, 0), P())
    f.set((1, 0, 0), S()); f.set((2, 0, 0), Block.observer(3))
    f.set((3, 0, 0), wblock(k, 2))                            # W, lands (4,0,0)
    f.set((4, 1, 0), P())                                     # P2
    f.set((5, 1, 0), H()); f.set((5, 0, 0), H())              # C2: honey (5,0,0) in front of W's landing cell
    return {'W': (5, 0, 0), 'ticks': 4}


def case_C(f, k):
    r = case_A(f, k)
    f.set((-1, 0, 3), RB()); f.set((0, 0, 3), P())           # PJ fires tick 0 too
    f.set((1, 0, 3), H()); f.set((2, 0, 3), H()); f.set((2, 0, 2), H())   # J's honey (2,0,2) touches W (2,0,1)
    return r


def case_D(f, k):
    r = case_A(f, k)
    f.set((-1, 0, 2), RB()); f.set((0, 0, 2), P())           # PJ
    f.set((1, 0, 2), H()); f.set((1, 0, 1), H())              # J: honey (1,0,1) moves INTO W's cell (2,0,1)
    return r


def case_E(f, k):
    f.set((-1, 0, 0), RB()); f.set((0, 0, 0), P())           # P1 (tick 0) carries W to (3,0,1)
    f.set((1, 0, 0), S()); f.set((2, 0, 0), S())
    f.set((2, 0, 1), wblock(k, 2))
    f.set((3, 1, 1), P())                                     # P2 powered by W from tick 2; pushes (4,1,1) honey
    f.set((4, 1, 1), H())                                     # C2 (does NOT touch W)
    # P3 also powered from tick 2 by W? no: P3 powered by its own observer chain is hard; use W too:
    f.set((3, -1, 1), P())                                    # P3 below W's landing cell, powered by W as well
    f.set((4, -1, 1), H()); f.set((4, 0, 1), H())             # C3: honey (4,0,1) touches W -> P3's push carries W
    # (4,0,1) honey also touches (4,1,1) honey of C2: honey-honey sticks!  keep C2 apart:
    f.remove((4, 1, 1)); f.set((4, 1, 1), S())                # C2 slime: honey/slime do not stick
    return {'W': (4, 0, 1), 'ticks': 4, 'P2fires': True}


def case_F(f, k):
    """negative control: W rests on idle segment's glue while that segment moves -> dragged (hazard is real)."""
    f.set((-1, 0, 0), RB()); f.set((0, 0, 0), P())
    f.set((1, 0, 0), S()); f.set((2, 0, 0), S())
    f.set((2, 0, 1), wblock(k, 2))
    return {'W': (3, 0, 1), 'ticks': 2}


def case_G(f, k):
    if k != 'O': return None
    f.set((-1, 0, 0), RB()); f.set((0, 0, 0), P())
    f.set((1, 0, 0), S()); f.set((2, 0, 0), S())
    f.set((2, 0, 1), Block.observer(2))                       # faces +Y; after landing at (3,0,1) faces P2 (3,1,1)
    f.set((3, 1, 1), P()); f.set((4, 1, 1), H())              # C2 not touching W
    return {'W': (3, 0, 1), 'ticks': 6, 'G': True}


CASES = {'A': case_A, 'B': case_B, 'C': case_C, 'D': case_D, 'E': case_E, 'F': case_F, 'G': case_G}


def run(builder, k, seed, px, pz):
    f = Flyer(phase_x=px, phase_z=pz, rng_state=seed, push_limit=12)
    spec = builder(f, k)
    if spec is None: return None, None
    tmp = pathlib.Path(tempfile.gettempdir()) / f'pr_fix_{seed}_{px}_{pz}'
    a, b = tmp.with_suffix('.in.flyer'), tmp.with_suffix('.out.flyer')
    f.save(a)
    res = {}
    for T in range(1, spec['ticks'] + 1):
        subprocess.run([str(EXE), str(a), str(b), '1'], check=True, capture_output=True)
        g = Flyer.load(b)
        res[T] = anchor(g)
        a, b = b, a
    return spec, res


def anchor(g):
    """saving renormalises coordinates: re-anchor on P1 (the minimum stationary piston, at (0,0,0) in every rig)."""
    cells = dict(g.blocks())
    p1 = min(p for p, bl in cells.items() if bl.kind == Kind.PISTON and p[1] == min(q[1] for q, b2 in cells.items() if b2.kind == Kind.PISTON and q[0] == min(r[0] for r, b3 in cells.items() if b3.kind == Kind.PISTON)) and p[0] == min(r[0] for r, b3 in cells.items() if b3.kind == Kind.PISTON))
    return {(p[0] - p1[0], p[1] - p1[1], p[2] - p1[2]): bl for p, bl in cells.items()}


def summary(cells):
    return tuple(sorted((p, b.kind.name, b.state if b.kind == Kind.PISTON else int(b.powered) if b.kind == Kind.OBSERVER else 0)
                        for p, b in cells.items()))


WK = {'R': Kind.REDSTONE_BLOCK, 'D': Kind.ROD, 'O': Kind.OBSERVER}

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    only = sys.argv[2].split(',') if len(sys.argv) > 2 else list(CASES)
    out = open(HERE / 'runs' / 'fixture.txt', 'a')
    for cname in only:
        builder = CASES[cname]
        for k in ('R', 'D', 'O'):
            trajs = Counter(); ex = {}
            for seed in range(n):
                for px in PHASES:
                    for pz in PHASES:
                        spec, res = run(builder, k, seed * 7919 + 13, px, pz)
                        if spec is None: break
                        key = tuple(summary(res[t]) for t in sorted(res))
                        trajs[key] += 1; ex[key] = (spec, res)
                    if spec is None: break
                if spec is None: break
            if not trajs: continue
            spec, res = ex[next(iter(trajs))]
            T = max(res); w = spec['W']
            wok = res[T].get(w) is not None and res[T][w].kind == WK[k]
            fires = {t: sorted(p for p, b in res[t].items() if b.kind == Kind.PISTON and b.state == 1) for t in sorted(res)}
            line = (f'case {cname} W={k}: {len(trajs)} distinct trajectory(ies) over {sum(trajs.values())} runs '
                    f'(seeds x 16 phases) | W at expected {w}: {wok} | extending pistons per tick {fires}')
            print(line, flush=True); out.write(line + chr(10))
            if len(trajs) > 1:
                for kk, c in trajs.items(): out.write(f'   {c} runs: final {kk[-1]}' + chr(10))
    out.close()
