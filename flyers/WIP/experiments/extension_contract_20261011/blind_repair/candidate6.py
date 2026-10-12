from pathlib import Path
import json, sys
repo=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(repo))
from fastflyer import Flyer, Block
exp=repo/'flyers'/'WIP'/'experiments'/'extension_contract_20261011'; out=exp/'blind_repair'/'out'
f=Flyer.load(exp/'out'/'missing_source.flyer'); f.set((12,4,9),Block(6)); f.set((14,6,9),Block(6)); f.save(out/'candidate6.flyer')
c=json.loads((exp/'benchmarks'/'missing_source.json').read_text()); c['name']='missing_source_blind_assisted_6'; c['flyer']='candidate6.flyer'; (out/'candidate6.json').write_text(json.dumps(c,indent=2)+'\n')
