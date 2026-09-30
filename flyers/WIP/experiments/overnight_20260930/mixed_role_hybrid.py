"""Close push/push/pull backs with pull/push/push fronts and glazed power."""
from pathlib import Path
import json
h=Path(__file__).resolve().parent
front=next(m for m in json.loads((h/'pull_first_movingcontacts_manifest.json').read_text())['candidates'] if m['file']=='dy12_dz0_s001.flyer');delta=front['delta']
def point(p):return [p[a]+delta[a] for a in range(3)]
frontcover=dict(delta=delta,patches=[[],[point((2,2,0))],[],[point((-1,0,0))],[point(p) for p in ((2,1,-1),(-1,1,-1),(-1,2,-1))],front['segments'][5]],pistons=front['pistons'][-3:],sources=front['sources'][-3:],glazed=front['glazed'])
(h/'pull_first_contact_cover.json').write_text(json.dumps(frontcover,indent=2))
s=(h/'mixed_role_ring.py').read_text().replace('mixed_tile_contact_cover.json','compact_mixed_tile_contact_cover.json').replace('mixed_extension_manifest.json','mixed_extension_compact_manifest.json').replace('dy12_dz0_s001.flyer','dy12_dz0_s000.flyer')
s=s.replace('mixed_role_ring_v2','mixed_role_hybrid').replace('mixed_role_ring_legal.py','mixed_role_hybrid_legal.py').replace('for radius in (8,10):','for radius in (6,7):').replace('cap=50','cap=40').replace('range(8)','range(4)')
s=s.replace('def main():',"backcover=cover;frontcover=json.loads((HERE/'pull_first_contact_cover.json').read_text())\ndef main():")
s=s.replace("ns=model.__dict__.copy();ns.update(S=S,DISP=DISP,K=K)","""source=source.replace('  w={}','  w={shift(p,DISP[owner][t]):Block(Kind.GLAZED_TERRACOTTA) for p,owner in GLAZED}')\n    gate=''' for t in range(5):
  for pp,dp,f,target,sticky in ps:
   ext=(f-1)%5 if sticky else f
   if t==ext:continue
   base=shift(pp,dp[t])
   for gp,gowner in GLAZED:
    solid=shift(gp,DISP[gowner][t])
    if solid==shift(base,-1 if sticky else 1) or sum(abs(a-b) for a,b in zip(base,solid))!=1:continue
    for rp,owner,observer,direction in sources:
     if observer and S[owner][(t-1)%5] and add(shift(rp,DISP[owner][t]),D[direction])==solid:return None,'glazed_cross_power'
'''
    source=source.replace(' @functools.lru_cache(None)',gate+' @functools.lru_cache(None)')\n    ns=model.__dict__.copy();ns.update(S=S,DISP=DISP,K=K,GLAZED=[])""")
s=s.replace('ss=[set() for _ in S];ps=[];sources=[]','ss=[set() for _ in S];ps=[];sources=[];glazed=[];ns[\'GLAZED\']=glazed')
s=s.replace('phase=(3*node)%5;q=',"cover=frontcover if node%2 else backcover;origin=cover['delta'];helpermap=({4:(node+3)%10,3:(node+1)%10,1:(node-3)%10} if node%2 else {2:(node-1)%10,3:(node+1)%10,4:(node+3)%10})\n                    phase=(3*node)%5;q=")
s=s.replace("for p in lead['segments'][5]","for p in cover['patches'][5]").replace('for oldowner,helpernode in ((2,(node-1)%10),(3,(node+1)%10),(4,(node+3)%10)):', 'for oldowner,helpernode in helpermap.items():')
s=s.replace('newowner=node if owner==5 else (node+3)%10','newowner=node if owner==5 else helpermap[owner]')
marker="                        sources.append((point(p,model.DISP[oldowner][phase]-model.DISP[0][phase]),newowner,observer,direction))"
s=s.replace(marker,marker+"\n                    for p,owner in cover.get('glazed',[]):glazed.append((point(p,model.DISP[owner][phase]-model.DISP[0][phase]),helpermap[owner]))")
s=s.replace('f=Flyer(rng_state=5,push_limit=1000)',"f=Flyer(rng_state=5,push_limit=1000)\n                    for p,owner in glazed:f._cells[p]=Block(Kind.GLAZED_TERRACOTTA)")
s=s.replace('pistons=ps,sources=sources,fronts=','pistons=ps,sources=sources,glazed=glazed,fronts=')
# The local origin changes per interface; make it a closure rather than the
# module-level origin used by the homogeneous reference builder.
s=s.replace('x,y,z=rotate(local(raw),q)','x,y,z=rotate(tuple(raw[a]-origin[a] for a in range(3)),q)')
target=h/'derived_mixed_role_hybrid.py';target.write_text(s)
exec(compile(s,str(target),'exec'),dict(__file__=str(target),__name__='__main__'))
