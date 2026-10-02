"""Track persistent identities through runner text sources, finding first bridge."""
import json,re,sys
from pathlib import Path
from search import OUT,canonical,Block,Kind,Flyer,shift
seed=int(sys.argv[1]) if len(sys.argv)>1 else 28
meta=next(m for m in json.loads((OUT/'manifest.json').read_text())['layouts'] if m['seed']==seed)
path=OUT/'candidates'/f's{seed}_diagnostic_pl512.flyer'
fly=Flyer.load(path)
original={tuple(p):f'core{i}' for i,s in enumerate(meta['segments']) for p in s}
for rp,i,d,f in meta['sources']:original[tuple(rp)]=f'core{i}'
for p,f,a in meta['pistons']:
 x,s,o=canonical(0,f,a);original[(x,p[1],p[2])]=f'P{f}'
offset=tuple(min(p[k] for p in fly._cells)-min(p[k] for p in original) for k in range(3))
ident={tuple(p[k]+offset[k] for k in range(3)):v for p,v in original.items()}
assert all(p in fly._cells for p in ident),offset
coord=re.compile(r'Coord \{ x: (-?\d+), y: (-?\d+), z: (-?\d+) \}')
def coords(line):return [tuple(map(int,m)) for m in coord.findall(line)]
text=(OUT/f's{seed}.trace.txt').read_text(encoding='utf-8-sig').splitlines()
actions=[];tick=-1
for line in text:
 if line.startswith('TICK '):tick=int(line.split()[1])
 if line.startswith('ACTION '):actions.append(dict(tick=tick,line=line,sources=[],links=[]))
 elif line.startswith('SOURCE '):actions[-1]['sources']+=coords(line)
 elif line.startswith('LINK '):actions[-1]['links'].append((line.split()[1],*coords(line)))
events=[];first=None
for a in actions:
 if 'sources=0 ' in a['line'] or 'failure=None' not in a['line']:continue
 counts={}
 for p in a['sources']:
  who=ident.get(p,'unknown');counts[who]=counts.get(who,0)+1
 cores={w for w in counts if w.startswith('core')}
 event=dict(tick=a['tick'],actor=a['line'],counts=counts)
 if len(cores)>1 and first is None:
  bridges=[]
  for link,p,q in a['links']:
   ip,iq=ident.get(p,'unknown'),ident.get(q,'unknown')
   if ip!=iq and iq in cores and (ip in cores or ip.startswith('P')):
    bridges.append(dict(kind=link,source=p,source_identity=ip,destination=q,destination_identity=iq))
  first=dict(**event,bridges=bridges)
 entries=[(p,ident.pop(p,'unknown')) for p in a['sources']]
 for p,w in entries:ident[shift(p,1)]=w
 events.append(event)
report=dict(seed=seed,normalization=offset,first_multiple_core_action=first,events=events)
(OUT/f's{seed}.diagnosis.json').write_text(json.dumps(report,indent=2))
print(json.dumps(first,indent=2))
