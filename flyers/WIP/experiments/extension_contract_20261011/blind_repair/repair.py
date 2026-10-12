from pathlib import Path
import json, shutil
root=Path(__file__).resolve().parents[1]
src=root/'out'/'missing_source.flyer'
base=root/'benchmarks'/'missing_source.json'
out=root/'blind_repair'/'out'
out.mkdir(parents=True,exist_ok=True)
shutil.copyfile(src,out/'candidate.flyer')
c=json.loads(base.read_text())
c['name']='missing_source_blind_repair'
c['flyer']='candidate.flyer'
(out/'candidate.json').write_text(json.dumps(c,indent=2)+'\n')
