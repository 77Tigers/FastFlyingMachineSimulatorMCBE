"""Rebuild and screen the banked PL43 geometry through the parameterized copy."""
from pathlib import Path
import sys, json, hashlib
ROOT=Path(__file__).resolve().parents[4]
EASY=Path(__file__).resolve().parents[0].parent/'mv4_easy_20261004'
sys.path.insert(0,str(EASY))
import common as c
import builder
from fastflyer import Flyer

OUT=Path(__file__).resolve().parent
source=EASY/'compact43/reroute_best.json'
meta=json.loads(source.read_text())
parent=meta['parent']
config=dict(own=parent['own'],previous=parent['previous'])
routes=[set(map(tuple,s)) for s in meta['segments']]
if not c.valid(routes,c.capture(meta)):
    raise SystemExit('Saved control routes fail existing physical checks')
placement=(meta['centers'],meta['rotations'],meta['reflections'])
ans,why=builder.build(0,placement,cap=max(map(len,routes)),
                     joint_router=lambda *args:routes,config=config)
if ans is None:raise SystemExit(f'Control builder failed: {why}')
flyer,rebuilt=ans
flyer.push_limit=43
path=OUT/'control_pl43.flyer';flyer.save(path)
bank=ROOT/'flyers/bank/pl43/mv4_symmetric_easy_compact.flyer'
same_hash=Flyer.load(path).content_hash()==Flyer.load(bank).content_hash()
if not same_hash:raise SystemExit('Rebuilt flyer differs from the banked control')
screen_pass=c.screen(path,ticks=300)
result=dict(control=str(path),source=str(bank),same_content_hash=same_hash,
            short80_pass=screen_pass,counts=rebuilt['counts'],
            baseline_sha256=hashlib.sha256(bank.read_bytes()).hexdigest(),
            config=rebuilt['config'],placement=placement)
c.write_json(OUT/'control.json',result)
print(json.dumps({k:v for k,v in result.items() if k not in ('config','placement')}),flush=True)
if not screen_pass:raise SystemExit('Control failed corrected short80 core screen')
