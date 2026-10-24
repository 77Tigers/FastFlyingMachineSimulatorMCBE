"""Lane maps of a flyer, one per x layer (x = the flight axis): python tools/flyer_slices.py FILE [--bodies]
Glue bodies (same-material face-connected slime / honey components) are labelled A, B, ... by mean x (then y, z),
the same order hoptrace uses; other blocks: p = piston, s = sticky piston (upper case P / S when extended),
r = redstone block, a = piston arm, o = observer, | = rod, # = other. Rows are y, columns z.
--bodies also lists every body's cells per x layer as (y, z) lanes."""
import sys, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from fastflyer import Flyer, Kind

D6 = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def bodies(fl):
    glue = {c: b.kind for c, b in fl.blocks() if b.kind in (Kind.SLIME, Kind.HONEY)}
    seen, comps = set(), []
    for c in sorted(glue):
        if c in seen: continue
        comp, st = [], [c]
        while st:
            u = st.pop()
            if u in seen: continue
            seen.add(u); comp.append(u)
            for d in D6:
                v = (u[0] + d[0], u[1] + d[1], u[2] + d[2])
                if v in glue and glue[v] == glue[c] and v not in seen: st.append(v)
        comps.append(comp)
    key = lambda cs: (sum(p[0] for p in cs) / len(cs), sum(p[1] for p in cs) / len(cs), sum(p[2] for p in cs) / len(cs))
    comps.sort(key=key)
    lab = {}
    for i, cs in enumerate(comps):
        name = chr(ord('A') + i) if i < 26 else chr(ord('a') + i - 26)
        for c in cs: lab[c] = name
    return lab, comps


def char(b):
    if b.kind == Kind.PISTON:
        c = 's' if b.sticky else 'p'
        return c.upper() if b.state else c
    return {Kind.REDSTONE_BLOCK: 'r', Kind.PISTON_ARM: 'a', Kind.OBSERVER: 'o', Kind.ROD: '|'}.get(b.kind, '#')


def main():
    path = sys.argv[1]
    fl = Flyer.load(path)
    blocks = dict(fl.blocks())
    lab, comps = bodies(fl)
    xs = [c[0] for c in blocks]; ys = [c[1] for c in blocks]; zs = [c[2] for c in blocks]
    for x in range(min(xs), max(xs) + 1):
        print(f'x = {x}')
        for y in range(min(ys), max(ys) + 1):
            row = ''
            for z in range(min(zs), max(zs) + 1):
                c = (x, y, z)
                row += lab[c] if c in lab else char(blocks[c]) if c in blocks else '.'
            print('   ', row)
    if '--bodies' in sys.argv:
        for i, cs in enumerate(comps):
            byx = collections.defaultdict(list)
            for c in cs: byx[c[0]].append((c[1], c[2]))
            print(lab[cs[0]], len(cs), {x: sorted(v) for x, v in sorted(byx.items())})


if __name__ == '__main__':
    main()
