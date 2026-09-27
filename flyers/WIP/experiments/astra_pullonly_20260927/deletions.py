from pathlib import Path
import sys,itertools,subprocess,re,json
sys.path.insert(0,'.');from fastflyer import Flyer,Kind
out=Path('flyers/WIP/experiments/astra_pullonly_20260927');dest=out/'deletions';dest.mkdir(exist_ok=True);f=Flyer.load(out/'mwmw_best.flyer');meta=[]
for i,(p,b) in enumerate(f.blocks()):
 if b.kind not in (Kind.SLIME,Kind.HONEY):continue
 for limit in (9,100):
  g=Flyer.from_bytes(f.to_bytes());g.remove(p);g.push_limit=limit;name=f'd{i}_pl{limit}.flyer';g.save(dest/name);meta.append(dict(file=name,removed=p,limit=limit))
(out/'deletions_metadata.json').write_text(json.dumps(meta,indent=2))
r=subprocess.run(['flyers/WIP/experiments/bin/research_runner.exe','batch',str(dest),'160'],capture_output=True,text=True);(out/'deletions_screen.txt').write_text(r.stdout)
print('tests',len(meta));print('\n'.join(s for s in r.stdout.splitlines() if 'distance=40 ' in s))
