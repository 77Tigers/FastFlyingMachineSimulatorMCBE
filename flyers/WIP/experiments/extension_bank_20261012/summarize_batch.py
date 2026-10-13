#!/usr/bin/env python3
"""Print a digest of contracts/<id>/<subdir>/results.json (subdir default `search`)."""
import glob, json, os, sys
sub = sys.argv[1] if len(sys.argv) > 1 else 'search'
base = os.path.dirname(os.path.abspath(__file__)) + '/contracts'
for rf in sorted(glob.glob(f'{base}/*/{sub}/results.json')):
    d = json.load(open(rf))
    s = d.get('summary') or {}
    b = s.get('best') or {}
    seed = s.get('seed_score') or {}
    print(f"== {d['id']} orders={d['orders']} own={d['own_recurrence']} search={d['search_recurrence']} ref_end={d['ref_endogenous_max']} "
          f"(seed all={d['seed_own'].get('all_max_load')} count={d['seed_own'].get('count_at_max')} blocks={d['seed_own'].get('blocks')} presc={d['seed_own'].get('max_prescribed_input_load')})")
    print(f"   evals={s.get('evaluations')} passing={s.get('passing_evaluations')} eps={s.get('evals_per_sec')} pareto={len(s.get('pareto', []))}")
    print(f"   best: excess={b.get('excess')} end_max={b.get('max_load')} all_max={b.get('all_max_load')} count={b.get('count_at_max')} blocks={b.get('blocks')} presc={b.get('max_prescribed_input_load')}")
    print(f"   diff: {b.get('diff_vs_seed')}")
    for c in d.get('confirm', []):
        py = {k: (v['single'][:4] + ' ' + v.get('samples', '')) for k, v in c['python'].items()}
        rs = {k: v for k, v in c['rust'].items() if 'samples' in k or '8cycles' in k}
        print(f"   [{c['file']}] seed={c['is_seed']} blocks={c['blocks']} limit={c['limit']}\n      rust={rs}\n      py={py}")
