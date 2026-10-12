from pathlib import Path
import json, sys
repo=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(repo))
from fastflyer import Flyer, Block
exp=repo/'flyers'/'WIP'/'experiments'/'extension_contract_20261011'; trial=exp/'blind_repair'; out=trial/'out'
base=json.loads((exp/'benchmarks'/'missing_source.json').read_text())
f=Flyer.load(out/'candidate3.flyer'); f.set((14,4,7),Block.piston(0)); f.save(out/'candidate4.flyer')
c=dict(base); c['name']='missing_source_blind_assisted_4'; c['flyer']='candidate4.flyer'
(out/'candidate4.json').write_text(json.dumps(c,indent=2)+'\n')
