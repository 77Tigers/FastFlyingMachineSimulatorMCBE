from pathlib import Path
import json, subprocess, sys
repo=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(repo))
from fastflyer import Flyer, Block, Kind
exp=repo/'flyers'/'WIP'/'experiments'/'extension_contract_20261011'; trial=exp/'blind_repair'
src=exp/'out'/'missing_source.flyer'; out=trial/'out'; out.mkdir(parents=True,exist_ok=True)
base=json.loads((exp/'benchmarks'/'missing_source.json').read_text())
f=Flyer.load(src); f.set((12,4,6),Block(Kind.REDSTONE_BLOCK)); f.save(out/'candidate1.flyer')
c=dict(base); c['name']='missing_source_blind_assisted_1'; c['flyer']='candidate1.flyer'
(out/'candidate1.json').write_text(json.dumps(c,indent=2)+'\n')
ds=[json.loads(x) for x in subprocess.check_output(['target/release/extension-trace.exe',str(src),'4','0','0','0'],text=True).splitlines()]
for tick,d in enumerate(ds):
 cells={tuple(row[:3]):row[3] for row in d['initial']}
 for s in d['steps']:
  if s['stage']=='piston':
   actor=s.get('active_piston')
   if actor and all(abs(actor[i]-(12,4,7)[i])<=2 for i in range(3)):
    a=tuple(actor); block=cells.get(a,0); state=(block>>10)&3; direction=(block>>5)&7
    adjacent=[]
    for p,cell in cells.items():
     if sum(abs(p[i]-a[i]) for i in range(3))!=1: continue
     kind=cell&15
     if kind in (6,8): adjacent.append((p,'redstone' if kind==6 else 'rod'))
     elif kind==7: adjacent.append((p,'observer',bool(cell&256),'facing',((cell>>5)&7)))
    m=s.get('movement') or {}
    print(f"tick={tick} actor={a} action={s['action']} state={state} facing={direction} adjacent_power_sources={adjacent}")
    if m.get('sources'):
     print('  sources=',m['sources'])
     print('  stick_links=',[x for x in m.get('links',[]) if x[2]=='stick'])
  for row in s['changes']:
   p=tuple(row[:3]); cell=row[3]
   if cell is None: cells.pop(p,None)
   else: cells[p]=cell
