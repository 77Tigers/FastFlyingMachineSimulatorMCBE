"""ASCII renderer for flyer designs stored as pickles ({'sol': [(name, word, cells, material), ...]}).

Usage: python render.py PKL [--slots 0,1,2,3] [--names K4,K5,V,F] [--x 6,15] [--moves]
Token = segment id + kind: glue 's'(slime)/'h'(honey), P, S, R, D<dir>, O<dir>; '.' empty; '!!' collision.
Dir chars: > +x, < -x, ^ +y, v -y, + +z, - -z.  Position at slot t = cells shifted by wpos(word, t) in x.
"""
import argparse
import pickle
import sys

ARROW = '><^v+-'
# digits then uppercase letters that cannot be confused with kind letters P S R D O
IDS = '0123456789ABCEFGHIJKLMNQTUVWXYZ'


def wpos(word, t):
    return sum(1 for m in word if m < t)


def parse_kind(kind, material):
    """-> (letter, dir or None): 'g'->s/h, P/S/R, ('D',d), 'D4'."""
    if isinstance(kind, (tuple, list)):
        return str(kind[0]), int(kind[1])
    if kind == 'g':
        return ('s' if material == 'slime' else 'h'), None
    if len(kind) == 2 and kind[0] in 'DO' and kind[1].isdigit():
        return kind[0], int(kind[1])
    return kind, None


def token(kind, material, sid):
    letter, d = parse_kind(kind, material)
    return sid + letter + (ARROW[d] if d is not None else '')


def placed(seg, t):
    """Cells of a segment at the start of slot t: {(x,y,z): kind}."""
    _, word, cells, _ = seg
    dx = wpos(word, t)
    return {(x + dx, y, z): k for (x, y, z), k in cells.items()}


def render(sol, slots=(0, 1, 2, 3), names=None, xr=None):
    ids = {s[0]: IDS[i % len(IDS)] for i, s in enumerate(sol)}  # stable ids, independent of filter
    segs = [s for s in sol if names is None or s[0] in names]
    out = ['Legend: ' + ', '.join('%s=%s%s' % (ids[s[0]], s[0], tuple(s[1])) for s in segs),
           'Cell = id+kind (s slime, h honey, P, S, R, D/O + dir ' + ARROW + '), . empty, !! collision', '']
    allp = [(t, p) for t in slots for s in segs for p in placed(s, t)]
    if not allp:
        return '\n'.join(out + ['(no cells)'])
    ys = [p[1] for _, p in allp]
    zs = [p[2] for _, p in allp]
    x0, x1 = tuple(xr) if xr else (min(p[0] for _, p in allp), max(p[0] for _, p in allp))
    y0, y1 = min(ys), max(ys)
    for t in slots:
        grid, bad = {}, {}
        for s in segs:
            for p, k in placed(s, t).items():
                tok = token(k, s[3], ids[s[0]])
                if p in grid:
                    bad.setdefault(p, [grid[p][1]]).append((s[0], tok))
                else:
                    grid[p] = (tok, (s[0], tok))
        out.append('=== slot %d ===' % t)
        zl = sorted({p[2] for p in grid if x0 <= p[0] <= x1})
        if not zl:
            out.append('(no cells in x range)')
        for z in zl:
            out.append('z=%d' % z)
            out.append('     ' + ''.join('%-4d' % x for x in range(x0, x1 + 1)) + ' (x)')
            for y in range(y1, y0 - 1, -1):
                row = ''.join('%-4s' % ('!!' if (x, y, z) in bad else grid[(x, y, z)][0] if (x, y, z) in grid else '.')
                              for x in range(x0, x1 + 1))
                out.append('y=%-3d' % y + row.rstrip())
            for p in sorted(bad):
                if p[2] == z and x0 <= p[0] <= x1:
                    out.append('  COLLISION at %s: %s' % (p, ', '.join('%s(%s)' % c for c in bad[p])))
            out.append('')
        ncol = sum(1 for p in bad if x0 <= p[0] <= x1)
        out.append('collisions in slot %d: %d' % (t, ncol))
        out.append('')
    return '\n'.join(out)


def moves(sol, slots=(0, 1, 2, 3), names=None):
    return '\n'.join('slot %d moves: %s' % (t, ' '.join(s[0] for s in sol
                     if (names is None or s[0] in names) and t in s[1]) or '(none)') for t in slots)


def main(argv=None):
    ap = argparse.ArgumentParser(description='ASCII render of a flyer pickle')
    ap.add_argument('pkl')
    ap.add_argument('--slots', default='0,1,2,3')
    ap.add_argument('--names', default=None, help='comma list of segment names')
    ap.add_argument('--x', default=None, help='xmin,xmax')
    ap.add_argument('--moves', action='store_true', help='print which segments move per slot')
    a = ap.parse_args(argv)
    with open(a.pkl, 'rb') as f:
        sol = pickle.load(f)['sol']
    slots = tuple(int(v) for v in a.slots.split(','))
    names = set(a.names.split(',')) if a.names else None
    xr = tuple(int(v) for v in a.x.split(',')) if a.x else None
    if a.moves:
        print(moves(sol, slots, names))
        print()
    print(render(sol, slots, names, xr))


if __name__ == '__main__':
    main()
