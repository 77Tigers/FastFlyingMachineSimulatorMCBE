"""Generic configuration runner for satflyer: chain templates + free bodies + free riders (+ merges).

A config is a dict:
  segs: list of dicts, one per segment:
     {'name', 'tmpl': K}                         alt-chain template segment K (orientation ORIENTS[0], origin as alt.py)
     {'name', 'free': K or (x,y,z), 'word'}      free body in a box around template K's origin (or a point)
     {'name', 'rider': 'P'|'S', 'word', 'near': K or (x,y,z)}   free single-piston rider
     optional 'open': flags (see satflyer open_segs), 'keep': True (template cells required for a free K)
  box: (x0, x1, r) box offsets around each free segment's centre; load; kinds; automerge; merges; mergeable
Usage from Python: run(cfg, tl, workers) -> (status, solution, model).  CLI: python cfgsat.py CONFIG_NAME [LOAD]
(named configs live in CONFIGS below; results go to runs/cfg/).
"""
import sys, pathlib, os, pickle, time, itertools
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'rigid_chain_20261003'))
from satflyer import FlyerSAT, Infeasible, show, to_rigid, add, WORDS
from chainflyer import ORIENTS, template, origins
from modules import BND_BACK, BND_FRONT

O1 = ORIENTS[0]
ORG = origins(12, *O1)
KALL = ('g', 'P', 'S', 'R', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'O0', 'O1', 'O2', 'O3', 'O4', 'O5')
KOBS = ('g', 'P', 'S', 'R', 'O0', 'O1', 'O2', 'O3', 'O4', 'O5')


def tcells(K):
    cells, word = template(K, *O1)
    return {add(ORG[K], u): k for u, k in cells.items()}, word


def centre(c): return ORG[c] if isinstance(c, int) else tuple(c)


def build(cfg):
    x0, x1, r = cfg.get('box', (-3, 4, 2))
    names, words, fixed, boxes, opens, riders, kbs, must = [], [], [], [], {}, [], {}, {}
    for i, s in enumerate(cfg['segs']):
        names.append(s['name'])
        if 'tmpl' in s:
            cells, w = tcells(s['tmpl']); words.append(w); fixed.append((cells, None)); boxes.append(None)
        else:
            c = centre(s.get('free', s.get('near')))
            words.append(WORDS[s['word']] if isinstance(s['word'], str) else s['word'])
            fixed.append(None)
            rx = s.get('box', (x0, x1, r))
            boxes.append([add(c, (dx, dy, dz)) for dx in range(rx[0], rx[1] + 1)
                          for dy in range(-rx[2], rx[2] + 1) for dz in range(-rx[2], rx[2] + 1)])
            if 'rider' in s:
                riders.append(s['name']); kbs[s['name']] = [s['rider']]
            if s.get('keep') and isinstance(s.get('free'), int):
                K = s['free']; cells, _ = tcells(K)
                must[s['name']] = {cc: k for cc, k in cells.items() if k in s.get('keepkinds', 'gPSR')}
            if 'kinds' in s: kbs[s['name']] = list(s['kinds'])
        if 'open' in s: opens[i] = s['open']
    M = FlyerSAT(words, None, cfg['load'], kinds=cfg.get('kinds', KOBS), leaf=True, maxglue=cfg['load'] - 1,
                 fixed=fixed, names=names, boxes=boxes, open_segs=opens, riders=riders, kinds_by_seg=kbs,
                 automerge=cfg.get('automerge', False), mergeable=cfg.get('mergeable'), merges=cfg.get('merges', ()),
                 must=must)
    return M


def report(M):
    sv = M.solver
    out = ['loads ' + str({f'{j if isinstance(j, int) else j}@{t}': sv.Value(e) for (j, t), e in M.loadexpr.items()})]
    out.append('merges ' + str([(t, M.names[a], M.names[b]) for (t, a, b), v in M.mg.items() if v is True or sv.Value(v)]))
    out.append('riders ' + str([(t, M.names[r], M.names[j]) for (t, r, j), v in M.rc.items() if sv.Value(v)]))
    return '\n'.join(out)


def run(cfg, tl=600, workers=16, objective=None, tag=None, hint=None):
    t0 = time.time()
    try:
        M = build(cfg)
    except Infeasible as e:
        return 'TRIVIAL_INFEASIBLE', None, None
    if hint is not None: M.hint(hint)
    st, dt = M.solve(tl, workers, objective=objective)
    sol = M.extract() if st in ('OPTIMAL', 'FEASIBLE') else None
    if sol is not None and tag:
        od = HERE / 'runs' / 'cfg'; od.mkdir(parents=True, exist_ok=True)
        pickle.dump({'sol': sol, 'cfg': cfg, 'riders': sorted(M.names[r] for r in M.riders)}, open(od / f'{tag}.pkl', 'wb'))
    return st, sol, M


def rider_seg(name, kind, word, near): return {'name': name, 'rider': kind, 'word': word, 'near': near}


# ---------------------------------------------------------------- named configs
def back_cfg(extra, load, nfree=2, automerge=True, kinds=KOBS, box=(-3, 4, 2)):
    """chain start: K0..K(nfree-1) free (template words), K(nfree)..K4 templates, K4 boundary; plus `extra` segs."""
    segs = []
    for K in range(5):
        w = 'mmww' if K % 2 == 0 else 'wwmm'
        if K < nfree: segs.append({'name': f'K{K}', 'free': K, 'word': w})
        else: segs.append({'name': f'K{K}', 'tmpl': K})
    segs[4]['open'] = BND_FRONT
    return {'segs': segs + extra, 'load': load, 'automerge': automerge, 'kinds': kinds, 'box': box}


def front_cfg(extra, load, nfree=2, automerge=True, kinds=KOBS, box=(-3, 4, 2), last=6):
    """chain end: K2..K(last) with K2 boundary; the last nfree are free; plus `extra` segs."""
    segs = []
    for K in range(2, last + 1):
        w = 'mmww' if K % 2 == 0 else 'wwmm'
        if K > last - nfree: segs.append({'name': f'K{K}', 'free': K, 'word': w})
        else: segs.append({'name': f'K{K}', 'tmpl': K})
    segs[0]['open'] = BND_BACK
    return {'segs': segs + extra, 'load': load, 'automerge': automerge, 'kinds': kinds, 'box': box}


if __name__ == '__main__':
    pass
