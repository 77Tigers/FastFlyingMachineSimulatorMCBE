#!/usr/bin/env python3
"""Confirm contract-search finalists: Rust `advance` check (80 samples, 8 cycles) and the Python checker in
`bounded` mode with a tight envelope (permanent-block bbox of the finalist, margin 0 and 1), both orders.

usage: python confirm_finalists.py SEARCH_DIR BASE_CONTRACT.json [--samples]
Run from the repository root. Writes contracts into SEARCH_DIR/confirm/.
"""
import glob, json, os, subprocess, sys

sys.path.insert(0, '.')
from fastflyer import Flyer

search_dir, base_contract = sys.argv[1], sys.argv[2]
do_samples = '--samples' in sys.argv
exe = os.path.abspath('target/release/contract-search.exe')
base = json.load(open(base_contract))
base_dir = os.path.dirname(os.path.abspath(base_contract))
out = os.path.join(search_dir, 'confirm')
os.makedirs(out, exist_ok=True)
script_abs = os.path.abspath(os.path.join(base_dir, base['prescribed_script']))

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout.strip()

for f in sorted(glob.glob(os.path.join(search_dir, '*.flyer'))):
    name = os.path.basename(f)[:-6]
    fl = Flyer.load(f)
    pos = [p for p, b in fl.blocks() if b.kind.name != 'PISTON_ARM']
    lo = [min(p[i] for p in pos) for i in range(3)]
    hi = [max(p[i] for p in pos) for i in range(3)]
    print(f'== {name}  limit={fl.push_limit} blocks={len(pos)}')
    # Rust: advance mode, 80 samples, 3 and 8 cycles, each order
    for cyc in (3, 8):
        for o in ('before', 'after'):
            # Rust needs a contract file: reuse a copy with flyer path rewritten
            c = dict(base)
            c['flyer'] = os.path.relpath(os.path.abspath(f), out).replace('\\', '/')
            c['prescribed_script'] = os.path.relpath(script_abs, out).replace('\\', '/')
            cp = os.path.join(out, f'{name}_rust.json')
            json.dump(c, open(cp, 'w'), indent=1)
            res = run([exe, cp, '0', '1', 'x', '--eval-only', '--samples', '--recurrence', 'advance', '--order', o, '--cycles', str(cyc)])
            d = json.loads(res)
            print(f'  rust advance cycles={cyc} order={o}: samples {d["samples_passed"]}/{d["samples_total"]} max_load={d["max_load"]}')
    # Python: bounded, tight envelope, both orders
    for margin in (0, 1):
        for o in ('before_natural', 'after_natural'):
            c = dict(base)
            c['flyer'] = os.path.relpath(os.path.abspath(f), out).replace('\\', '/')
            c['prescribed_script'] = os.path.relpath(script_abs, out).replace('\\', '/')
            c['prescribed_order'] = o
            c['recurrence'] = 'bounded'
            c['boundary_envelope'] = {'min': [lo[i] - margin for i in range(3)], 'max': [hi[i] + margin for i in range(3)]}
            c['name'] = f'{name}-{o}-env{margin}'
            cp = os.path.join(out, f'{name}_{o}_env{margin}.json')
            json.dump(c, open(cp, 'w'), indent=1)
            r = subprocess.run(['python', 'tools/extension_contract.py', cp], capture_output=True, text=True)
            line = r.stdout.strip()
            ok = ': PASS' in line
            extra = ''
            if do_samples and ok:
                r2 = subprocess.run(['python', 'tools/extension_contract.py', cp, '--samples'], capture_output=True, text=True)
                extra = ' | samples: ' + r2.stdout.strip().split('(')[1].split(';')[0]
            tail = line.split('whole max action=')[-1][:70] if ok else line.split('—')[-1][:140]
            print(f'  python bounded env+{margin} {o}: {"PASS" if ok else "FAIL"} max_action={tail}{extra}')
