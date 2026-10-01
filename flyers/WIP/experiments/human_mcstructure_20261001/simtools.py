"""Batch helpers around bin/research_runner.exe (screen/verify/samples). Run from anywhere."""
import subprocess, pathlib, csv, shutil, sys, io, uuid
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUNNER = ROOT / 'flyers/WIP/experiments/bin/research_runner.exe'

def screen(flyers, ticks=400, workdir=None, keep=False):
    """flyers: {name: Flyer}. Saves each, runs `screen`, returns {name: row dict}."""
    wd = pathlib.Path(workdir) if workdir else HERE / 'work' / f'screen_{uuid.uuid4().hex[:8]}'
    if wd.exists(): shutil.rmtree(wd, ignore_errors=True)
    wd.mkdir(parents=True, exist_ok=True)
    for n, f in flyers.items(): f.save(wd / f'{n}.flyer')
    out = wd.parent / (wd.name + '.csv')
    subprocess.run([str(RUNNER), 'screen', str(wd), str(ticks), '--out', str(out)], check=True,
                   capture_output=True, text=True, cwd=ROOT)
    rows = {}
    for r in csv.DictReader(open(out, newline='')):
        rows[pathlib.Path(r['file']).stem] = r
    if not keep:
        shutil.rmtree(wd, ignore_errors=True)
        try: out.unlink()
        except OSError: pass
    return rows

def brief(r):
    return (f"dist={r['distance']:>5} load={r['max_successful_action']:>3} ext={r['extensions']:>6} "
            f"extfail={r['extension_failures']} movefail={r['movement_failures']} "
            f"cons={r['conservation_mismatch_ticks']} clean={r['clean']}")

def run(cmd, *args):
    p = subprocess.run([str(RUNNER), cmd, *map(str, args)], capture_output=True, text=True, cwd=ROOT)
    return p.returncode, p.stdout + p.stderr
