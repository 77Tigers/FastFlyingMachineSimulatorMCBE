"""Body graph of a flyer (who pushes / pulls / carries whom): python tools/flyer_graph.py FILE PERIOD_SLOTS
Needs target/release/hoptrace and flyer-ledger (cargo build --release --manifest-path tools/Cargo.toml --target-dir target).
Bodies = same-material glue components (hoptrace labels A, B, ... by mean x), with their words (m = moves).
Edges (from hoptrace's per-slot roles over one period, after a warm-up):
  X =rigid=> Y   a piston that only rides X pushes Y            X =pull=> Y   a sticky on X pulls Y (ledger)
  Y <=hop[Z]     a hopper of Y (fires on Y) carried by Z between firings (Z = '-' if never carried)"""
import sys, re, subprocess, collections, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
EXE = '.exe' if sys.platform == 'win32' else ''
HOP = ROOT / f'target/release/hoptrace{EXE}'
LED = ROOT / f'target/release/flyer-ledger{EXE}'


def graph(fl, P, warm=30):
    out = subprocess.run([str(HOP), fl, str(warm + 2 * P), str(warm), str(2 * P)], capture_output=True, text=True).stdout
    words, sizes, rows = {}, {}, []
    for l in out.splitlines():
        m = re.match(r'body (\w) = (\d+) (\w+)', l)
        if m: sizes[m.group(1)] = (int(m.group(2)), m.group(3)); continue
        m = re.match(r'word (\w) (\w+)', l)
        if m: words[m.group(1)] = m.group(2); continue
        m = re.match(r'\s*(\d+) (\S+)\s+(.*)', l)
        if m and m.group(2) in ('P+x', 'S-x', 'RB', 'P-x', 'S+x', 'OB', 'ROD') or (m and m.group(2) not in ('pow',) and len(m.group(3).split()) == P):
            cells = m.group(3).split()
            if len(cells) == P and m.group(2) != 'pow': rows.append((m.group(2), cells))
    E = collections.Counter(); powers = collections.Counter()
    for kind, cells in rows:
        fires = [c[1] for c in cells if c[0] == 'F' and c[1] != '-']
        rides = [c[1] for c in cells if c[0] == 'r']
        if kind == 'RB': powers[('RB', ''.join(sorted(set(rides))))] += 1; continue
        if kind.startswith('S'): continue    # stickies: victims from the ledger
        for y in fires:
            car = sorted(set(rides) - {y})
            if set(rides) <= {y} | set(car) and y not in rides and len(set(rides)) == 1 and rides:
                E[(rides[0], 'rigid', y)] += 1
            else:
                E[(''.join(car) or '-', 'hop', y)] += 1
    # pulls from the ledger (body names differ: map by size+material is unreliable, so match by moved glue cells)
    return words, sizes, E, powers


if __name__ == '__main__':
    fl, P = sys.argv[1], int(sys.argv[2])
    words, sizes, E, powers = graph(fl, P)
    for b in sorted(words): print(f'{b}: {sizes[b][0]:2d} {sizes[b][1]:5s} word {words[b]}')
    print('edges:')
    for (a, k, b), c in sorted(E.items(), key=lambda e: (e[0][2], e[0][1])):
        print(f'  {b} <= {k}[{a}] x{c}' if k == 'hop' else f'  {a} =rigid=> {b} x{c}')
    print('redstone blocks by carrier body:', dict(powers))
