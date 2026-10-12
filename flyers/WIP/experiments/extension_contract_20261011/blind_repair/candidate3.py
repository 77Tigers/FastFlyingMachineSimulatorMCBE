from pathlib import Path
import json, sys
repo=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(repo))
from fastflyer import Flyer, Block, Kind
exp=repo/'flyers'/'WIP'/'experiments'/'extension_contract_20261011'; trial=exp/'blind_repair'; out=trial/'out'
src=exp/'out'/'missing_source.flyer'; base=json.loads((exp/'benchmarks'/'missing_source.json').read_text())
f=Flyer.load(src); f.set((12,4,9),Block(Kind.REDSTONE_BLOCK)); f.save(out/'candidate3.flyer')
c=dict(base); c['name']='missing_source_blind_assisted_3'; c['flyer']='candidate3.flyer'
(out/'candidate3.json').write_text(json.dumps(c,indent=2)+'\n')
