"""Bounded front rerouting on Sol's repeating sticky-pull rear carrier."""
from pathlib import Path
import os, subprocess, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from fastflyer import Block, Flyer, Kind

base = Flyer.load(ROOT / 'flyers/WIP/experiments/sol_pl12/rear_route/lead1_pl14.flyer')
out = Path(os.environ['TEMP']) / 'n2_hybrid_front_route'
out.mkdir(exist_ok=True)
run = Path(os.environ['TEMP']) / 'flyer_batch.exe'
front = [p for p,b in base._cells.items() if b.kind == Kind.SLIME]
mandatory = (14,1,17)
others = [p for p in front if p != mandatory]
additions = [None] + [
    (x,y,z) for x in range(14,21) for y in range(0,4) for z in range(14,20)
    if (x,y,z) not in base._cells
]
folder = out / 'pl12'
folder.mkdir(exist_ok=True)
names = {}
for second in others:
    for add in additions:
      for kind in ((Kind.SLIME,) if add is None else (Kind.SLIME,Kind.HONEY,Kind.SMOOTH_STONE,Kind.GLAZED_TERRACOTTA)):
        f = Flyer(rng_state=2, push_limit=12)
        f._cells = base._cells.copy()
        del f._cells[mandatory]
        del f._cells[second]
        if add is not None:
            f._cells[add] = Block(kind)
        tag = f'd{second[0]}_{second[1]}_{second[2]}_a' + ('none' if add is None else '_'.join(map(str,add))) + f'_k{int(kind)}'
        path = folder / f'{tag}.flyer'
        try:
            f.save(path)
            names[tag] = (second,add)
        except Exception:
            pass
print('generated', len(names), flush=True)
q = subprocess.run([str(run), '160', str(folder)], capture_output=True, text=True)
rows=[]
for line in q.stdout.splitlines():
    parts=line.split('\t')
    if len(parts)>=2:
        try: rows.append((int(parts[1]),parts[0],line))
        except ValueError: pass
print('screened',len(rows),'best',*sorted(rows,reverse=True)[:30],sep='\n',flush=True)
