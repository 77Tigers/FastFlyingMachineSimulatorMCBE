import os as _research_os
from pathlib import Path
import json, subprocess, sys
repo=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(repo))
from fastflyer import Flyer, Block, Kind
exp=repo/'flyers'/'WIP'/'experiments'/'extension_contract_20261011'; trial=exp/'blind_repair'; out=trial/'out'
src=exp/'out'/'missing_source.flyer'; base=json.loads((exp/'benchmarks'/'missing_source.json').read_text())
f=Flyer.load(src); f.set((13,4,9),Block(Kind.REDSTONE_BLOCK)); f.save(out/'candidate2.flyer')
c=dict(base); c['name']='missing_source_blind_assisted_2'; c['flyer']='candidate2.flyer'
(out/'candidate2.json').write_text(json.dumps(c,indent=2)+'\n')
# Print only the two candidate actuator histories from trace.
ds=[json.loads(x) for x in subprocess.check_output([('target/release/extension-trace' + ('.exe' if _research_os.name == 'nt' else '')),str(out/'candidate2.flyer'),'4','0','0','0'],text=True).splitlines()]
for ti,d in enumerate(ds):
 for s in d['steps']:
  if s['stage']=='piston' and s.get('active_piston') in ([12,4,7],[13,4,8]):
   m=s.get('movement') or {}; print('tick',ti,'actor',s['active_piston'],'action',s['action'],'move',len(m.get('sources',[])),'failure',m.get('failure'))
