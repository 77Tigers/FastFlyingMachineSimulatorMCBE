"""simulate a flyer at PL (1 seed, 1000 blocks): python simk.py FILE K PL -> prints nkcheck output"""
import sys, subprocess, pathlib
HERE = pathlib.Path(__file__).resolve().parent; NK = str(HERE / 'out/target/release/nkcheck.exe')
def flies(path, k, pl):
    P = 2 * (k + 2); n = -(-1000 // k) + 1
    out = subprocess.run([NK, str(path), str(n * P), '1000', '1', 'at', str(pl)], capture_output=True, text=True).stdout
    return f'minpl={pl}' in out, out.strip()
if __name__ == '__main__':
    ok, out = flies(sys.argv[1], int(sys.argv[2]), int(sys.argv[3])); print(ok, out[-300:])
