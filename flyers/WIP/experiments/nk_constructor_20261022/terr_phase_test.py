import sys, os, subprocess, json
k, w = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, 0)
from concurrent.futures import ProcessPoolExecutor
def run(ph):
    env = dict(os.environ, TERR_PH=str(ph))
    out = subprocess.run([sys.executable, '-c', f"""
import families as F
r = F.build({k}, {w}); L = r.T.L; m = L // 4
bad = r.check(sorted({{(X + d) % L for X in (0, 1, m) for d in range(-2, 3)}}))
print(F.predicted_pl(r) if not bad else 'bad', max(r.size()), min(r.size()))
"""], capture_output=True, text=True, env=env).stdout.strip()
    return ph, out
if __name__ == '__main__':
    with ProcessPoolExecutor(14) as ex:
        for ph, out in ex.map(run, range(int(sys.argv[3]))): print(ph, out, flush=True)
