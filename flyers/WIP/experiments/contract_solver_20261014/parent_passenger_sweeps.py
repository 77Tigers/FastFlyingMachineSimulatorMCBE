"""Fixed-parent passenger destination witnesses; immovable adjacency alone is not a collision."""
import os as _research_os
import json,subprocess,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def main():
 base=HERE/'out/quarter_ring_contacts/T1_sticky_on_G1_transfer';out=HERE/'out/quarter_ring_contacts/H0_passenger_sweeps';out.mkdir(exist_ok=True);assert not (out/'report.json').exists()
 ports={tuple(p['at']):p['name'] for p in json.loads((base/'before_natural.json').read_text(encoding='utf-8'))['ports']};records=[]
 for order in ['before','after','interleaved']:
  p=subprocess.run([str(ROOT/('target/release/extension-prescribe' + ('.exe' if _research_os.name == 'nt' else ''))),str(base/'problem.flyer'),'30',str(base/'drive.txt'),order,'0','0','7'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',check=True)
  (out/f'{order}.jsonl').write_text(p.stdout,encoding='utf-8');rows=[json.loads(line) for line in p.stdout.splitlines()];origins={tuple(c[:3]):tuple(c[:3]) for c in rows[0]['trace']['initial'] if c[3]&15!=10}
  for row in rows:
   if row['tick']>=10:break
   for step in row['trace']['steps']:
    move=step.get('movement') or {};assert not move.get('failure');src=list(map(tuple,move.get('sources',[])));dst=list(map(tuple,move.get('destinations',[])))
    if not src or not dst:continue
    assert len(src)==len(dst);names=sorted({ports[origins[q]] for q in src if origins.get(q) in ports})
    if names and names!=['H0_front']:
     for q,d in zip(src,dst):
      if q in origins:records.append({'slot':row['tick']//2,'order':order,'ports':names,'from':q,'to':d,'origin':origins[q]})
    entries={d:origins[q] for q,d in zip(src,dst) if q in origins}
    for q in src:origins.pop(q,None)
    origins.update(entries)
 result={'scope':__doc__+' Conditional on retaining verified parent passenger trajectories; not a general impossibility proof. Three order traces, single rng/phase.','base_sha256':hashlib.sha256((base/'problem.flyer').read_bytes()).hexdigest(),'records':records};(out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'records':len(records),'G0_slot1_collision_witnesses':[r for r in records if r['slot']==1 and r['to']==(19,2,13)]}))
if __name__=='__main__':main()
