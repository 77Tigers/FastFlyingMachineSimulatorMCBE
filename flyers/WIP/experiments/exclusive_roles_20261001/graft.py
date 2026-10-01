"""Graft a passive, exclusively pulled body onto an unchanged running engine.
New stickies ride existing rigid bodies and use existing redstone timing.
All candidates have encoded PL24; only isolated own output files are written.
"""
import sys, re, subprocess, itertools, json, collections, random
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind,DIRECTIONS
def sx(p,x):return (p[0]+x,p[1],p[2])
def nb(p):return [tuple(a+b for a,b in zip(p,d)) for d in DIRECTIONS]
def offset(w,k):return sum(x=='m' for x in w[:k])

def main(base,L,outname):
    base=Path(base);out=HERE/outname;out.mkdir(exist_ok=True)
    flyer=Flyer.load(base)
    raw=subprocess.check_output([str(HERE/'states.exe'),str(base),str(2*L)],text=True)
    W=[{} for k in range(L+1)]
    for line in raw.splitlines():
        t,x,y,z,cell=map(int,line.split());W[t//2][x,y,z]=Block.decode(cell)
    import os
    env=dict(os.environ,BT_CELLS='1')
    txt=subprocess.check_output([str(HERE.parent/'bin/human_bodytrack.exe'),str(base),str(8*L),str(2*L),str(2*L)],text=True,env=env)
    (out/'bodies.txt').write_text(txt)
    bodies=[]
    for line in txt.splitlines():
        m=re.match(r'  B(\d+): n=(\d+).*word=([mw]+)',line)
        if m: current=(int(m[1]),int(m[2]),m[3])
        if 'cells:' in line:
            cells={tuple(map(int,m[:3])):m[3] for m in re.findall(r'\((-?\d+),(-?\d+),(-?\d+)\)(\S+)',line)}
            if any(v in ('sl','ho') for v in cells.values()):bodies.append((current[0],current[2],cells))
    candidates={s:[] for s in range(L)}
    for bi,w,cells in bodies:
        glue={p for p,v in cells.items() if v in ('sl','ho')}
        own=[{sx(p,offset(w,k)) for p in cells} for k in range(L)]
        gkind=flyer._cells[next(iter(glue))].kind
        positions=set()
        for k in range(L):
            if w[k]=='m' or w[(k+1)%L]=='m':continue
            for r,b in W[k].items():
                if b.kind==Kind.REDSTONE_BLOCK:
                    positions.update(sx(q,-offset(w,k)) for q in nb(r) if q!=sx(r,1))
        for p in positions - set(flyer._cells):
            if min(sum(abs(a-b) for a,b in zip(p,g)) for g in glue)>7:continue
            power=[];ok=True
            for k in range(L):
                q=sx(p,offset(w,k));world=W[k]
                if q in world:ok=False;break
                if any(world.get(r,Block(Kind.GLASS)).kind==Kind.REDSTONE_BLOCK for r in nb(q) if r!=sx(q,-1)):power.append(k)
                if w[k]=='m':
                    if sx(q,1) in world and sx(q,1) not in own[k]:ok=False;break
                    for r in nb(q):
                        b=world.get(r)
                        if b and b.kind in (Kind.SLIME,Kind.HONEY) and r not in own[k]:ok=False;break
            if not ok or len(power)!=1:continue
            f=power[0];s=(f+1)%L
            if w[f]=='m' or w[s]=='m':continue
            if any(sx(p,offset(w,k)-1) in W[k] for k in (f,s)):continue
            def support_ok(c):
                for k in range(L):
                    q=sx(c,offset(w,k));world=W[k]
                    if q in world and q not in own[k]:return False
                    if q==sx(p,offset(w,k)):return False
                    if k in (f,s) and q==sx(p,offset(w,k)-1):return False
                    if w[k]=='m' and sx(q,1) in world and sx(q,1) not in own[k]:return False
                    for r in nb(q):
                        b=world.get(r)
                        if b is None or r in own[k]:continue
                        if b.kind==gkind:return False
                        if w[k]=='m' and b.kind not in (Kind.SLIME,Kind.HONEY,Kind.GLAZED_TERRACOTTA,Kind.PISTON_ARM):
                            if b.kind!=Kind.PISTON or (b.state==0 and not b.moving):return False
                return True
            # Glue must reach the sticky from a side, never through its arm.
            starts=[c for c in nb(p) if c!=sx(p,-1) and (c in glue or support_ok(c))]
            queue=collections.deque(starts);prev={c:None for c in starts};depth={c:1 for c in starts};hit=None
            while queue:
                c=queue.popleft()
                if c in glue:hit=c;break
                if depth[c]>=6:continue
                for q in nb(c):
                    if q in prev:continue
                    if q not in glue and not support_ok(q):continue
                    prev[q]=c;depth[q]=depth[c]+1;queue.append(q)
                if len(prev)>600:break
            if hit is None:continue
            extra=set();c=hit
            while c is not None:
                if c not in glue:extra.add(c)
                c=prev[c]
            candidates[s].append(dict(p=p,body=bi,w=w,f=f,s=s,extra=sorted(extra),gkind=int(gkind)))
    print('candidate rigid pullers by slot',{s:len(v) for s,v in candidates.items()},flush=True)
    (out/'ports.json').write_text(json.dumps(candidates,indent=2))
    def legal(c,tw,kind,ports):
        for k in range(L):
            q=sx(c,offset(tw,k));world=W[k];moving=tw[k]=='m'
            if q in world:return False
            if moving and sx(q,1) in world:return False
            for r in nb(q):
                b=world.get(r)
                if b and (b.kind==kind or b.kind not in (Kind.SLIME,Kind.HONEY,Kind.GLAZED_TERRACOTTA)):
                    return False
            for p in ports:
                pp=sx(p['p'],offset(p['w'],k))
                for c2 in p['extra']:
                    q2=sx(c2,offset(p['w'],k))
                    if q==q2 or (moving and sx(q,1)==q2):return False
                    if p['gkind']==int(kind) and q2 in nb(q):return False
                if q==pp:return False
                if k==p['s'] and q==sx(pp,-1):return False
                if moving and sx(q,1)==pp:return False
                if moving and pp in nb(q) and k not in (p['f'],p['s']):return False
                if k==p['f'] and q==sx(pp,-1):return False
                if moving and k==p['s'] and sx(q,1)==sx(pp,-1):
                    # Own pull contact is allowed to enter the removed arm cell.
                    if q!=sx(pp,-2):return False
        return True
    count=0;combos=0;legalfaces=0
    for slots in itertools.combinations(range(L),L-2):
        if any(not candidates[s] for s in slots):continue
        tw=''.join('m' if k in slots else 'w' for k in range(L))
        for ports in itertools.product(*(candidates[s] for s in slots)):
            combos+=1
            if len({p['p'] for p in ports})!=len(ports):continue
            faces={sx(p['p'],offset(p['w'],p['s'])-offset(tw,p['s'])-2) for p in ports}
            for kind in (Kind.SLIME,Kind.HONEY):
                if not all(legal(c,tw,kind,ports) for c in faces):continue
                legalfaces+=1
                rail={min(faces)};left=faces-rail;failed=False
                while left:
                    prev={c:None for c in rail};queue=collections.deque(rail);hit=None
                    while queue:
                        c=queue.popleft()
                        if c in left:hit=c;break
                        for q in nb(c):
                            if q in prev:continue
                            if min(sum(abs(a-b) for a,b in zip(q,r)) for r in faces)>12:continue
                            if not legal(q,tw,kind,ports):continue
                            prev[q]=c;queue.append(q)
                        if len(prev)>1800:break
                    if hit is None:failed=True;break
                    c=hit
                    while c not in rail:rail.add(c);c=prev[c]
                    left-=rail
                    if len(rail)>24:failed=True;break
                if failed:continue
                g=Flyer.load(base);g.push_limit=24
                overlap=False
                for p in ports:
                    for c in p['extra']:
                        c=tuple(c)
                        if c in g._cells and g._cells[c].kind!=Kind(p['gkind']):overlap=True
                        g.set(c,Block(Kind(p['gkind'])))
                if overlap:continue
                for c in rail:g.set(c,Block(kind))
                for p in ports:
                    g.set(p['p'],Block.piston(1,sticky=True,state=2 if p['s']==0 else 0))
                    if p['s']==0:g.set(sx(p['p'],-1),Block(Kind.PISTON_ARM))
                name=f'c{count:04d}';g.save(out/(name+'.flyer'))
                (out/(name+'.json')).write_text(json.dumps(dict(ports=ports,word=tw,rail=sorted(rail),kind=int(kind)),indent=2))
                count+=1;print(name,tw,'rail',len(rail),flush=True)
                if count>=80:break
            if count>=80:break
        if count>=80:break
    print('done',dict(combinations=combos,legal_face_sets=legalfaces,candidates=count),flush=True)

if __name__=='__main__':main(sys.argv[1],int(sys.argv[2]),sys.argv[3])
