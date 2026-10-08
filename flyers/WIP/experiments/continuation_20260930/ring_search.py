"""Bounded route-seed search; sustained speed is distinct from exact recurrence."""
from pathlib import Path
import sys, importlib.util, subprocess, csv, json

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent
RUNNER = ROOT / 'target/release/fastflyer-research.exe'
spec = importlib.util.spec_from_file_location('derived', HERE.parent / 'sol_reference_20260928/derived_generator.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def main():
    manifest = []
    for n, copies, centers in [
        (3, 1, [(0,0),(0,4),(3,5),(5,2),(3,-1)]),
        (4, 1, [(0,0),(0,4),(3,1)]),
        (4, 2, [(0,0),(0,4),(2,6),(6,6),(6,2),(4,0)]),
    ]:
        dest = HERE / f'ring_n{n}_copies{copies}'
        dest.mkdir(exist_ok=True)
        for seed in range(96):
            ans = module.make(n, centers, seed, 100)
            if ans is None:
                manifest.append(dict(n=n, copies=copies, seed=seed, routed=False))
                continue
            f, counts, _ = ans
            path = dest / f's{seed:03}.flyer'
            f.save(path)
            manifest.append(dict(n=n, copies=copies, seed=seed, routed=True, counts=counts))
        screen = HERE / f'ring_n{n}_copies{copies}_screen.csv'
        p = subprocess.run([str(RUNNER), 'screen', str(dest), '240', '--out', str(screen)], capture_output=True, text=True)
        (HERE / f'ring_n{n}_copies{copies}_screen.txt').write_text(p.stdout+p.stderr)
        rows = list(csv.DictReader(screen.open()))
        good = [r for r in rows if r['clean']=='true' and int(r['distance'])==240*n//(2*(n+2))]
        good.sort(key=lambda r: (int(r['max_successful_action']), int(r['end_blocks']), r['file']))
        for r in good[:5]:
            f = __import__('fastflyer').Flyer.load(r['file'])
            f.push_limit = int(r['max_successful_action'])
            out = HERE / f"n{n}_copies{copies}_{Path(r['file']).stem}_pl{f.push_limit}.flyer"
            f.save(out)
            p = subprocess.run([str(RUNNER), 'verify', str(out), '10000', '--period', str(2*(n+2)), '--advance', str(n)], capture_output=True, text=True)
            out.with_suffix('.verify.txt').write_text(p.stdout+p.stderr)
            print(p.stdout.strip(), flush=True)
        (HERE/'ring_manifest.json').write_text(json.dumps(manifest, indent=2))
        print('family', n, copies, 'routed', len(rows), 'sustained', len(good), 'best', [(r['max_successful_action'],r['end_blocks']) for r in good[:5]], flush=True)

if __name__=='__main__': main()
