"""Check allowed A/B differences, including normalization during .flyer saving."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from fastflyer import Flyer,Kind,DIRECTIONS

def check(a,b,limit=12):
 fa,fb=Flyer.load(a),Flyer.load(b)
 def permanent(f):return {p:v for p,v in f.blocks() if v.kind!=Kind.PISTON_ARM}
 aa,bb=permanent(fa),permanent(fb)
 assert len(aa)==len(bb),'Different permanent block counts'
 offsets=(min(p[0] for p in aa)+max(p[0] for p in bb),min(p[1] for p in bb)-min(p[1] for p in aa),min(p[2] for p in bb)-min(p[2] for p in aa))
 changes=[]
 for p,v in aa.items():
  q=(offsets[0]-p[0],p[1]+offsets[1],p[2]+offsets[2]);w=bb.get(q)
  assert w is not None,f'Missing reflected block {p} -> {q}'
  assert v.kind==w.kind,(p,'kind')
  direction=v.direction^1 if v.kind in (Kind.PISTON,Kind.OBSERVER,Kind.ROD) and v.direction<2 else v.direction
  assert w.direction==direction,(p,'direction')
  assert v.sticky==w.sticky and v.angry==w.angry,(p,'piston type or angry bit')
  assert not v.moving and not w.moving,(p,'moving start')
  if v.state!=w.state or v.powered!=w.powered:changes.append({'A':p,'B':q,'kind':v.kind.name,'state':[v.state,w.state],'powered':[v.powered,w.powered]})
 for f in (fa,fb):
  expected=set()
  for p,v in f.blocks():
   assert not v.moving,'Moving block'
   if v.kind==Kind.PISTON:
    assert v.state in (0,2),'Piston transition state'
    assert not f.get_piston_blocks(p),'Nonempty movement owner list'
    if v.state==2:expected.add(tuple(p[i]+DIRECTIONS[v.direction][i] for i in range(3)))
  actual={p for p,v in f.blocks() if v.kind==Kind.PISTON_ARM}
  assert actual==expected,'Piston arm geometry disagrees with state'
 assert fa.push_limit==fb.push_limit==limit
 return {'pass':True,'push_limit':limit,'permanent_blocks':len(aa),'all_blocks_settled':True,'file_coordinate_map':{'x':'offset_x - A.x','offset':offsets},'state_changes':changes}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('A');ap.add_argument('B');ap.add_argument('--out');ap.add_argument('--limit',type=int,default=12);args=ap.parse_args()
 result=check(args.A,args.B,args.limit);s=json.dumps(result,indent=2)
 if args.out:Path(args.out).write_text(s+'\n')
 print(s)
