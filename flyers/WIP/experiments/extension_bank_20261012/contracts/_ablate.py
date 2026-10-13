"""scratch: try removing each input port (and its cells) from a contract's spec; report which still pass both orders"""
import sys, os, importlib.util, tempfile
from pathlib import Path
from n2_common import *
def load(n):
    spec = importlib.util.spec_from_file_location('b_'+n, f'{n}/build.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def trial(m, drop_ports=(), drop_cells=(), tag='t'):
    d = Path(os.environ['TEMP']) / f'abl_{tag}'; d.mkdir(exist_ok=True)
    keep = [k for k in m.KEEP if tuple(k) not in set(map(tuple, drop_cells))]
    sh = make_candidate(m.REF, keep, d / 'candidate.flyer')
    pin = [p for p in m.PORTS_IN if p['name'] not in drop_ports]
    pin = shift_ports(pin, sh); pout = shift_ports(m.PORTS_OUT, sh)
    (d / 'drive.txt').write_text("\n".join(drive_rows(pin)) + "\n")
    res = []
    for o in ('before_natural', 'after_natural'):
        write_contract(d, 'abl', o, pin, pout)
        res.append(check(d, o).split('(')[0].strip().endswith('PASS') or ': PASS' in check(d, o))
    return res
if __name__ == '__main__':
    n = sys.argv[1]; m = load(n)
    for p in m.PORTS_IN:
        cells = [p['at']]
        print(p['name'], trial(m, [p['name']], cells, p['name']))
