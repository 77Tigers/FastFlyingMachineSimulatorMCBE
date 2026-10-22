"""helpers: build a Ring, route, check, save, simulate with fastflyer-research (scratch copy)."""
import os as _research_os
import subprocess, re, sys, pathlib
from ring_designer import Ring, ORDER
import os
ROOT = pathlib.Path(__file__).resolve().parents[4]
BIN = os.environ.get("N6_RUNNER", str(ROOT / ('target/release/fastflyer-research' + ('.exe' if _research_os.name == 'nt' else ''))))
OUT = pathlib.Path(os.environ.get("N6_OUT", str(pathlib.Path(__file__).resolve().parent / "out")))
OUT.mkdir(exist_ok=True)


def sim(path, ticks=2000):
    r = subprocess.run([BIN, 'verify', str(path), str(ticks), '--period', '16', '--advance', '6'], capture_output=True, text=True)
    line = [l for l in r.stdout.splitlines() if l.startswith('verify')][-1]
    d = dict(kv.split('=', 1) for kv in line.split()[1:] if '=' in kv)
    return int(d['distance']), int(d['max_successful_action']), int(d['extension_failures']), d['first_failure_tick'], d.get('first_failure_kind', '')


def run(mod, place, tag, pl=60, extra=None, verbose=True):
    ring = Ring(mod, place, extra)
    for X in ORDER: ring.route(X)
    bad = ring.check()
    fl = ring.flyer(pl); p = OUT / f'{tag}.flyer'; fl.save(str(p))
    res = sim(p)
    if verbose: print(tag, ring.size(), 'checks', len(bad), bad[:3], 'sim', res)
    return ring, bad, res
