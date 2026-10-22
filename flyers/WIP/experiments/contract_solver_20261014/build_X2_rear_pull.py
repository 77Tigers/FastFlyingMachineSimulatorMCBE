"""Test one changed X2 contact with a T2-carried sticky and supplied G2 power.

The G2 source follows wwmmm; its three moves remain explicit inputs. This is
a loaded component test, not a complete flyer or a net reduction of inputs.
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
    glue, sticky, rb = (19, 6, 12), (21, 6, 12), (24, 6, 12)
    assert (18, 6, 12) in f._cells and (21, 6, 13) in f._cells
    for at, block in [(glue, Block(Kind.SLIME)),
                      (sticky, Block.piston(1, sticky=True)),
                      (rb, Block(Kind.REDSTONE_BLOCK))]:
        assert at not in f._cells, at
        f.set(at, block)
    f.save(a.out / 'problem.flyer')
    assert Flyer.load(a.out / 'problem.flyer')._cells == f._cells
    before = json.loads((a.base / 'before_natural.json').read_text(encoding='utf-8'))
    target = next(p for p in before['ports'] if p['name'] == 'X2')
    assert target['word'] == 'wmmmw' and target['provenance'][3] == 'supplied'
    remove = {(10 * cy + 6, target['at'][0] + 3 * cy + 2,
               target['at'][1], target['at'][2]) for cy in range(3)}
    old = [tuple(map(int, row.split())) for row in
           (a.base / 'drive.txt').read_text(encoding='utf-8').splitlines()]
    assert sum(row[:4] in remove for row in old) == 3
    rows = [row for row in old if row[:4] not in remove]
    for cy in range(3):
        for slot in (2, 3, 4):
            rows.append((10 * cy + 2 * slot, rb[0] + 3 * cy + slot - 2,
                         rb[1], rb[2], 1))
    (a.out / 'drive.txt').write_text(''.join(' '.join(map(str, row)) + '\n'
                                               for row in sorted(rows)), encoding='utf-8')
    for order in ('before_natural', 'after_natural', 'interleaved'):
        c = json.loads((a.base / f'{order}.json').read_text(encoding='utf-8'))
        c['name'] = a.out.name
        next(p for p in c['ports'] if p['name'] == 'X2')['provenance'][3] = 'internal'
        c['ports'].append({'name': 'G2_power', 'role': 'input', 'at': rb,
                           'word': 'wwmmm',
                           'provenance': [None, None, 'supplied', 'supplied', 'supplied']})
        (a.out / f'{order}.json').write_text(json.dumps(c, indent=2) + '\n', encoding='utf-8')
    prep = {'scope': __doc__, 'base': str(a.base), 'added_X2_glue': glue,
            'T2_sticky': sticky, 'supplied_G2_RB': rb, 'fire_slot': 2, 'pull_slot': 3,
            'sticky_word': 'mmwwm', 'source_word': 'wwmmm',
            'sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                       [a.base / 'problem.flyer', a.base / 'before_natural.json',
                        a.base / 'drive.txt', Path(__file__)]}}
    (a.out / 'preparation.json').write_text(json.dumps(prep, indent=2) + '\n', encoding='utf-8')
    r = subprocess.run([str(ROOT / ('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),
                        str(a.out / 'before_natural.json'), str(a.out / 'native.json'), '90', '2'],
                       cwd=ROOT, capture_output=True, text=True)
    assert (a.out / 'native.json').exists(), r.stderr
    report = json.loads((a.out / 'native.json').read_text(encoding='utf-8'))
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
