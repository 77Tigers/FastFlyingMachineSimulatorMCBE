"""Enumerate flat four-hopper handoffs and close short, alternating rings."""
import argparse
import ctypes
import itertools
import json
import sys
import os
import subprocess
import tempfile
from collections import defaultdict
from functools import cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'nk_constructor_20261022'))
from nk import Timing, Ring, D6, SYMS, add
from nk2 import power_problems
from stack import Ring3

D2 = [d[1:] for d in D6 if d[0] == 0]
EMPTY = dict(P=[], R=[], PLATE=[], CONT=[])
TIME = Timing(4, 6)
# 32-lane strides keep axial and lateral translations cheap in the link search.
STEPS = (1024, -1024, 32, -32, 1, -1)


def pos(x, y, z):
    return (x + 12) * 1024 + (y + 15) * 32 + z + 15


def xyz(i):
    return (i // 1024 - 12, (i // 32) % 32 - 15, i % 32 - 15)


def neighbours(p):
    return {(p[0] + y, p[1] + z) for y, z in D2}


def shape(pushers, red, covers):
    return tuple(sorted(pushers)), tuple(sorted(red)), tuple(sorted(covers))


def normalize(p, r, c):
    y0, z0 = min(l[0] for l in p), min(l[1] for l in p)
    return shape([(l[0]-y0,l[1]-z0,*l[2:]) for l in p], [(l[0]-y0,l[1]-z0,*l[2:]) for l in r],
                 [(x,y-y0,z-z0) for x,y,z in c])


def turn(data, sym):
    p, r, c = data
    def orient(l):
        extra=(l[2],*SYMS[sym](*l[3:])) if len(l)==5 else l[2:]
        return (*SYMS[sym](*l[:2]),*extra)
    return normalize([orient(l) for l in p], [orient(l) for l in r],
                     [(x,*SYMS[sym](y,z)) for x,y,z in c])


def module(data):
    p, r, c = data
    def at(l, dx): return (dx + (l[2] if len(l)>2 else 0), *l[:2])
    hard=[(l[2],l[0]+l[3],l[1]+l[4]) for l in r if len(l)==5]
    return dict(P=p, R=[at(l,0) for l in r], PLATE=[at(l,1) for l in p]+hard, CONT=c,
                RODS=[(at(l,0),l[3:]) for l in r if len(l)==5])


def templates(mode):
    variants = set()
    pairs = [[(0,0)], [(0,0),(0,1)], [(1,1),(-1,-1)]]
    if mode == 'wide':
        pairs.extend([[(0,0),(1,1)], [(0,0),(0,2)], [(0,0),(1,2)]])
    for c in pairs:
        ports = set.union(*(neighbours(l) for l in c)) - set(c)
        for pp in itertools.combinations(sorted(ports), 4):
            p = set(pp)
            for n in (1,2):
                if c == pairs[2] and n != 1: continue
                opts = set.union(*(neighbours(l) for l in p)) - p - set(c)
                for rr in itertools.combinations(sorted(opts), n):
                    if not all(p & neighbours(r) for r in rr): continue
                    if not p <= set.union(*(neighbours(l) for l in rr)): continue
                    template = normalize(p, rr, [(-2,*l) for l in c])
                    variants.add(min(turn(template,s) for s in range(8)))
    return sorted(variants)


@cache
def forbidden(data, own, t):
    # W (body 1) has origin x=0. Body 0 is its predecessor with origin -t.
    # Own outgoing pickup belongs to 2. Predecessor pickup belongs to W.
    mods = [EMPTY] * 6
    anchor = 1 if own else 0
    mods[anchor] = module(data)
    places = [(0,(0,0),0)] * 6
    places[0] = (-t,(0,0),0)
    ring = Ring(TIME, mods, places)
    worlds = ring.worlds()
    seen = set()
    for s, world in enumerate(worlds):
        dx = TIME.shift(1,s)
        for x,y,z in world:
            g = (x-dx,y,z)
            seen.add(g)
            seen.update(add(g,d) for d in D6)
    bad = set()
    for g in seen:
        if not ring.cell_ok(1,g,worlds):
            bad.add(pos(*g))
            continue
        # Ring.cell_ok permits a co-moving foreign redstone block.
        for s, world in enumerate(worlds):
            if not TIME.moves(1,s): continue
            point = (g[0] + TIME.shift(1,s), *g[1:])
            if any(q != 1 and k == 'RB' for d in D6 for q,k,_ in world.get(add(point,d),())):
                bad.add(pos(*g))
                break
    return bad


def components(cells):
    unseen = cells.copy()
    result = []
    while unseen:
        todo = [unseen.pop()]
        group = set(todo)
        while todo:
            v = todo.pop()
            for step in STEPS:
                w = v + step
                if w in unseen:
                    unseen.remove(w)
                    group.add(w)
                    todo.append(w)
        result.append(group)
    return result


@cache
def native_library(directional=False):
    source = HERE/'route.c'
    target = HERE/('.route_directed.so' if directional else '.route.so')
    if not target.exists() or target.stat().st_mtime_ns < source.stat().st_mtime_ns:
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            output = Path(directory)/'route.so'
            flags = ['-DRED_BRIDGE'] if directional else []
            subprocess.run(['cc','-O3','-shared','-fPIC',*flags,str(source),'-o',str(output)],check=True)
            os.replace(output,target)
    return ctypes.CDLL(str(target))


solver = native_library().route
solver.argtypes = [ctypes.c_int]*3 + [np.ctypeslib.ndpointer(np.int16),
                   np.ctypeslib.ndpointer(np.uint8),np.ctypeslib.ndpointer(np.int16),
                   np.ctypeslib.ndpointer(np.uint8)]


def link(v, w, t, dy, dz, limit, margin=1):
    """Positions and returned glue are in W's frame; W is (t,dy,dz) from V at V's rest."""
    vp, vr, vc = v
    wp, wr, wc = w
    capacity = limit - 4 - len(wr)
    # Even a tree with no obstacles must span all three coordinate ranges.
    points = [(1,*p) for p in wp] + [(x-t,y-dy,z-dz) for x,y,z in vc]
    low = list(map(min,zip(*points)))
    high = list(map(max,zip(*points)))
    if sum(b-a for a,b in zip(low,high))+1 > capacity: return
    vp = {(y-dy,z-dz) for y,z in vp}
    vr = {(y-dy,z-dz) for y,z in vr}
    if (vp|vr) & (set(wp)|set(wr)): return
    if any(neighbours(r) & vp for r in wr): return
    if any(neighbours(r) & set(wp) for r in vr): return
    required = {pos(*p) for p in points}
    a = forbidden(w,True,0)
    delta = dy*32+dz
    b = {i-delta for i in forbidden(v,False,t)}
    bad = a | b
    if required & bad: return
    groups = components(required)
    for y,z in wr:
        adj = {pos(0,y,z)+d for d in STEPS} - bad
        if not adj: return
        if not required & adj: groups.append(adj)
    low[0] = min(low[0],-1)
    nodes = [pos(x,y,z) for x in range(low[0]-margin,high[0]+margin+1)
             for y in range(low[1]-margin,high[1]+margin+1)
             for z in range(low[2]-margin,high[2]+margin+1) if pos(x,y,z) not in bad]
    idx = {v:i for i,v in enumerate(nodes)}
    edges = np.array([[idx.get(v+d,-1) for d in STEPS] for v in nodes], dtype=np.int16)
    cost = np.array([v not in required for v in nodes], dtype=np.uint8)
    members = np.zeros(len(nodes), dtype=np.int16)
    for j, cells in enumerate(groups):
        for cell in cells:
            if cell in idx: members[idx[cell]] |= 1 << j
    selected = np.zeros(len(nodes),dtype=np.uint8)
    extra = solver(len(nodes),len(groups),capacity-len(required),edges,cost,members,selected)
    if extra == 100: return
    glue = sorted(xyz(v) for i,v in enumerate(nodes) if selected[i] or v in required)
    assert len(glue) == extra + len(required)
    return glue


def scan(args):
    data = templates(args.mode)
    print(len(data),'template classes', flush=True)
    edges = []
    for i,v in enumerate(data):
        for j,base in enumerate(data):
            seen = set()
            for s in range(8):
                w = turn(base,s)
                if w in seen: continue
                seen.add(w)
                for t in args.offsets:
                    for y,z in itertools.product(range(-5,6), repeat=2):
                        glue = link(v,w,t,y,z,args.pl)
                        if glue:
                            edges.append(dict(i=i,j=j,s=s,t=t,dy=y,dz=z,g=glue))
        print(i, len(edges),'links',flush=True)
    Path(args.output).write_text(json.dumps(dict(templates=data,edges=edges)))
    for t in args.offsets:
        links = [e for e in edges if e['t'] == t]
        print(t,len(links), min((len(e['g'])+len(data[e['j']][1])+4 for e in links),default=None))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--mode',default='compact',choices=['compact','wide'])
    p.add_argument('--pl',type=int,default=17)
    p.add_argument('--offsets',type=int,nargs='+',default=[-1,0])
    p.add_argument('--output',default=str(HERE/'links.json'))
    scan(p.parse_args())
