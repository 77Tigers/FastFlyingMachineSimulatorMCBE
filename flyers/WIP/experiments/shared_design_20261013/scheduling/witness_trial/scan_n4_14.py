from __future__ import annotations
import os as _research_os
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]
folder=Path(__file__).parent/'n4_14_scan'
folder.mkdir(parents=True,exist_ok=True)
flyer=ROOT/'flyers/extension_bank/n4/n4_14/candidate.flyer'
script=ROOT/'flyers/extension_bank/n4/n4_14/drive.txt'
driver=ROOT/('target/release/extension-prescribe' + ('.exe' if _research_os.name == 'nt' else ''))
samples=[(rng,px,pz) for rng in (0,1,2,5,42) for px in (0,7,8,15) for pz in (0,7,8,15)]
failures=[]
for sample in samples:
 cmd=[str(driver),str(flyer),'36',str(script),'interleaved',*map(str,sample)]
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
 rows=[json.loads(line) for line in p.stdout.splitlines()]
 for row in rows:
  bad=[s for s in row['trace']['steps'] if s.get('stage')=='prescribed' and s.get('action')=='prescribed move failed']
  if not bad: continue
  steps=row['trace']['steps']
  for badstep in bad:
   index=steps.index(badstep)
   before=[s for s in steps[:index] if s.get('stage')=='piston' and s.get('action') not in (None,'idle')]
   after=[s for s in steps[index+1:] if s.get('stage')=='piston' and s.get('action') not in (None,'idle')]
   item={'sample':sample,'tick':row['tick'],'schedule_seed':row.get('schedule_seed'),'before':before,'failed':badstep,'after':after,'returncode':p.returncode}
   failures.append(item)
   if before and after:
    stem='_'.join(map(str,sample))
    (folder/f'trace_{stem}.jsonl').write_text(p.stdout,encoding='utf-8')
    (folder/f'stderr_{stem}.txt').write_text(p.stderr,encoding='utf-8')
    print('WITNESS',json.dumps(item),flush=True)
    (folder/'failures.json').write_text(json.dumps(failures,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0)
  print(f'fail {sample} tick {row["tick"]} before={len(before)} after={len(after)}',flush=True)
(folder/'failures.json').write_text(json.dumps(failures,indent=2)+'\n',encoding='utf-8')
print(f'no natural A->failed prescribed->natural B found; failures={len(failures)}')
