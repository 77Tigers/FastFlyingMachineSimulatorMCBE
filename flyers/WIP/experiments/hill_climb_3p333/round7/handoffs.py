"""Upper bounds on the X displacement of independently oriented handoffs."""
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from pathlib import Path
import json
import subprocess

HERE = Path(__file__).resolve().parent
FULL = (1, 3, 3)
NAMES = ('O3', 'T3', 'A3c')


def read_links():
    def run(args):
        output = subprocess.check_output([HERE / 'links', *map(str, args)], text=True)
        return [list(map(int, line.split()[:9])) for line in output.splitlines()]
    args = product(range(3), range(3), (8, 9, 10, 11, 12))
    with ThreadPoolExecutor(6) as pool:
        rows = [row for group in pool.map(run, args) for row in group]
    return {(a,b,cap,mask): t for a,b,cap,mask,t,*_ in rows}


def main():
    table = read_links()
    result = {}
    for caps in ((11,11,8)*2,(12,11,8,11,11,8),(11,12,8,11,11,8),
                 (11,11,9,11,11,8)):
        best, winners = -99, []
        for shapes in product(range(3), repeat=6):
            offsets = tuple(table[a,shapes[(i+1)%6],caps[(i+1)%6],FULL[a]]
                            for i,a in enumerate(shapes))
            total = sum(offsets)
            if total > best:
                best, winners = total, []
            if total == best:
                winners.append(dict(shapes=[NAMES[s] for s in shapes], offsets=offsets))
        result[str(caps)] = dict(maximum=best, witnesses=len(winners), first=winners[0])
    print(json.dumps(dict(whole=result, links=[[*k,v] for k,v in sorted(table.items())]), indent=1))


if __name__ == '__main__':
    main()
