"""Close the supplied G2 source with three normals and a changed T2 route.

T2 loses two redundant upper-branch cells, gains three pickup cells, and
carries all three G2 normals at slot1. Its optimistic budget is7 glue+RB+
X2 sticky+3 G2 normals=12. Native verification must check the actual loads.
G2 uses4 honey glue+its retained RB; other boundary inputs remain supplied.
"""
import os as _research_os
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from assemble import Flyer
from fastflyer import Block, Kind

ROOT = Path(__file__).resolve().parents[4]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base', type=Path)
    ap.add_argument('out', type=Path)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    f = Flyer.load(a.base / 'problem.flyer')
    removed = [(21, 5, 14), (22, 5, 14)]
    t2_added = [(22, 5, 13), (21, 7, 13), (22, 7, 13)]
    g2 = [(25, 6, 12), (25, 5, 12), (25, 7, 12), (25, 6, 13)]
    for p in removed:
        assert f._cells.pop(p).kind == Kind.SLIME
    added = {p: Block(Kind.SLIME) for p in t2_added}
    added.update({p: Block(Kind.HONEY) for p in g2})
    for p in [(22, 5, 12), (22, 7, 12)]:
        added[p] = Block.piston(0)
    added[(23, 6, 13)] = Block.piston(0, state=2)
    added[(24, 6, 13)] = Block(Kind.PISTON_ARM)
    assert not set(added) & set(f._cells)
    for p, b in added.items():
        f.set(p, b)
    f.save(a.out / 'problem.flyer')
    assert Flyer.load(a.out / 'problem.flyer')._cells == f._cells
    c = json.loads((a.base / 'before_natural.json').read_text(encoding='utf-8'))
    target = next(p for p in c['ports'] if p['name'] == 'G2_power')
    assert target['at'] == [24, 6, 12] and target['word'] == 'wwmmm'
    remove = {(10 * cy + 2 * s, 24 + 3 * cy + s - 2, 6, 12)
              for cy in range(3) for s in (2, 3, 4)}
    rows = [tuple(map(int, row.split())) for row in
            (a.base / 'drive.txt').read_text(encoding='utf-8').splitlines()]
    assert sum(row[:4] in remove for row in rows) == 9
    # The old T2 representative is one of the replaced glue cells. Keep the
    # supplied slot1 input anchored to retained glue in the same moving body.
    old_t2 = {(10 * cy + 2, 22 + 3 * cy, 5, 14) for cy in range(3)}
    assert sum(row[:4] in old_t2 for row in rows) == 3
    rows = [(*row[:3], 13, row[4]) if row[:4] in old_t2 else row for row in rows]
    (a.out / 'drive.txt').write_text(''.join(' '.join(map(str, row)) + '\n'
        for row in rows if row[:4] not in remove), encoding='utf-8')
    for order in ('before_natural', 'after_natural', 'interleaved'):
        c = json.loads((a.base / f'{order}.json').read_text(encoding='utf-8'))
        c['name'] = a.out.name
        p = next(p for p in c['ports'] if p['name'] == 'G2_power')
        p['provenance'] = [None, None, 'internal', 'internal', 'internal']
        next(p for p in c['ports'] if p['name'] == 'T2')['at'] = [21, 5, 13]
        (a.out / f'{order}.json').write_text(json.dumps(c, indent=2) + '\n', encoding='utf-8')
    info = {'scope': __doc__, 'base': str(a.base), 'removed_T2_glue': removed,
            'added_T2_glue': t2_added, 'G2_glue': g2,
            'added_cells': [[*p, b.encode()] for p, b in added.items()],
            'sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                       [a.base / 'problem.flyer', a.base / 'drive.txt',
                        a.base / 'before_natural.json', Path(__file__)]}}
    (a.out / 'preparation.json').write_text(json.dumps(info, indent=2) + '\n', encoding='utf-8')
    r = subprocess.run([str(ROOT / ('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),
                        str(a.out / 'before_natural.json'), str(a.out / 'native.json'), '90', '2'],
                       cwd=ROOT, capture_output=True, text=True)
    assert (a.out / 'native.json').exists(), r.stderr
    print((a.out / 'native.json').read_text(encoding='utf-8'), flush=True)


if __name__ == '__main__':
    main()
