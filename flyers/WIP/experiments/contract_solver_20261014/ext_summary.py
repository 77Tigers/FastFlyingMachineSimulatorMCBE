"""Summarise an extension-contract benchmark run by family: python ext_summary.py TAG"""
import csv, json, collections, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
tag = sys.argv[1]
fam = collections.defaultdict(lambda: [0, 0, 0, 0])
for r in csv.DictReader(open(HERE / f'runs/{tag}/results.csv')):
    fl, kind = r['id'].split('/')
    m = json.loads((HERE / f'flyerprobs_ext/{fl}/{kind}/problem_meta.json').read_text())
    k = (f"P{m['period']}/+{m['advance']}", 'ref' if m.get('reference_pass') is True else 'noref')
    f = fam[k]; f[0] += 1; f[1] += r['status'] == 'verified'
    if r['status'] == 'verified' and m.get('reference_pass') is True:
        f[2] += int(r['load']) <= int(m['reference_load']); f[3] += int(r['load']) < int(m['reference_load'])
        if int(r['load']) < int(m['reference_load']):
            print('BETTER', r['id'], m['reference_load'], '->', r['load'])
for k in sorted(fam): print(k, 'n=%d verified=%d <=ref=%d <ref=%d' % tuple(fam[k]))
t = [sum(v[i] for v in fam.values()) for i in range(4)]
print('total n=%d verified=%d <=ref=%d <ref=%d' % tuple(t))
