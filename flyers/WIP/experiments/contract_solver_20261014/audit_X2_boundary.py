"""Record provided-input obligations and one necessary G2 pickup diagnostic.

This is not a search or acceptance proof. The single-source ordinary-column
diagnostic fixes G2 power at24,6,12 and keeps all existing T2 glue unchanged.
"""
import argparse
import hashlib
import json
from pathlib import Path

from assemble import Flyer
from fastflyer import Kind


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('run', type=Path)
    a = ap.parse_args()
    f = Flyer.load(a.run / 'problem.flyer')
    c = json.loads((a.run / 'before_natural.json').read_text(encoding='utf-8'))
    t2 = [(21, 5, 14), (22, 5, 14), (21, 4, 14),
          (21, 4, 13), (21, 5, 13), (21, 6, 13)]
    assert all(f._cells[p].kind == Kind.SLIME for p in t2)
    rb = (24, 6, 12)
    assert next(p['at'] for p in c['ports'] if p['name'] == 'G2_power') == list(rb)
    offsets = [(-1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
    early = [tuple(v - o - (2 if k == 0 else 0)
                   for k, (v, o) in enumerate(zip(rb, off))) for off in offsets]
    pickup = [p for p in early if p not in f._cells and
              any(sum(abs(x - y) for x, y in zip(p, g)) == 1 for g in t2)]
    assert pickup == [(22, 6, 13)]
    internal = sum(s == 'internal' for p in c['ports'] for s in p['provenance'])
    supplied = sum(s == 'supplied' for p in c['ports'] for s in p['provenance'])
    assert (internal, supplied) == (19, 8)
    report = {'scope': __doc__, 'cells': len(f._cells),
              'internal_body_strokes': internal, 'supplied_original_body_strokes': 5,
              'new_G2_source_strokes': 3, 'ports': c['ports'],
              'G2_ordinary_column_prerequisite': {
                  'fixed_source': rb, 'early_normal_candidates': early,
                  'existing_T2_initial_pickup_candidates': pickup,
                  'implication': 'Two early normals need changed T2 support or a different power/carrier allocation. No whole-architecture impossibility claim.'},
              'sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                         [a.run / 'problem.flyer', a.run / 'before_natural.json', Path(__file__)]}}
    (a.run / 'boundary_obligations.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'internal': internal, 'supplied': supplied, 'supported_early_lanes': pickup}))


if __name__ == '__main__':
    main()
