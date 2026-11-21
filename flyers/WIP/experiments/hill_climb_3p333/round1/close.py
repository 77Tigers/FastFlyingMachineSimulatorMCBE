"""Close three successive links by rotation and screen the complete geometry."""
import argparse
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from functools import cache
from search import D6, Ring3, SYMS, Timing, add, module, power_problems, shape, HERE, turn


def plus(a,b): return a[0]+b[0],a[1]+b[1]
def minus(a,b): return a[0]-b[0],a[1]-b[1]


def composition(inner,outer):
    img=SYMS[outer](*SYMS[inner](1,2))
    return next(s for s in range(8) if SYMS[s](1,2)==img)


@cache
def origin(data,s):
    rotated=[SYMS[s](*l[:2]) for l in data[0]]
    return tuple(map(min,zip(*rotated)))


def candidate(data, edges, midsym, copies):
    L=3*copies
    timing=Timing(4,L)
    mods=[]; places=[]; incoming=[]; frame=(0,0); x=0; rot=0
    for i,e in enumerate(edges*copies):
        if i%3==0: previous=rot
        v,w=data[e['i']],data[e['j']]
        places.append((x,frame,rot)); mods.append(module(v))
        offset=(e['dy'],e['dz'])
        # Each edge describes positions in the predecessor's normalized, unrotated frame.
        rests=timing.rest[i]
        timing_offset=timing.shift(timing.nxt(i),rests)-timing.shift(i,rests)
        next_x=x+e['t']-timing_offset
        glue={(next_x+gx,*plus(frame,SYMS[rot](*plus(offset,(y,z)))))
              for gx,y,z in e['g']}
        incoming.append(glue)
        frame=plus(frame,SYMS[rot](*minus(offset,origin(w,e['s']))))
        rot=composition(e['s'],rot)
        x=next_x
        if i%3==2:
            expected=composition(midsym,previous)
            if rot!=expected:
                if turn(data[edges[0]['i']],rot)!=turn(data[edges[0]['i']],expected): return
                frame=plus(frame,minus(origin(data[edges[0]['i']],rot),origin(data[edges[0]['i']],expected)))
            rot=expected
    if x!=0 or frame!=(0,0): return
    r=Ring3(timing,mods,places,['slime' if i%2==0 else 'honey' for i in range(L)],[None]*L)
    r.glue=incoming[-1:]+incoming[:-1]
    return r


def rod_targets(r):
    for i,mod in enumerate(r.mods):
        for base, local_dir in mod.get('RODS',()):
            delta=SYMS[r.place[i][2]](*local_dir)
            yield i,r.mw(i,base,0),delta


def save_flyer(r,pl,target):
    from fastflyer import Block
    flyer=r.flyer(pl)
    for _,p,d in rod_targets(r):
        flyer.set(p,Block.rod(D6.index((0,*d))))
    flyer.save(str(target))


def driven_from_every_face(r,body):
    glue=r.glue[body]
    red={r.mw(body,p,0) for p in r.mods[body]['R']}
    all_cells=glue|red
    for face in r.mods[body]['PLATE'][:4]:
        start=r.mw(body,face,0)
        seen={start}
        todo=[start]
        while todo:
            p=todo.pop()
            for d in D6 if p in glue else ((1,0,0),):
                q=add(p,d)
                if q in all_cells and q not in seen:
                    seen.add(q)
                    todo.append(q)
        if seen!=all_cells: return False
    return True


def first_issue(r):
    # Reject every material overlap; include each possible order for the four ready pistons.
    for s in range(6):
        occ=r.world(s)
        for c,entities in occ.items():
            if len({owner for owner,_,_ in entities})>1:
                return 'overlap'
            # Every moving source, including a spent piston riding a foreign body, has a free
            # destination or pushes something already attached to its own moving body.
            for owner,k,info in entities:
                if k=='arm' or (k=='P' and info[1]==2): continue
                mover=r.carrier(owner,info[0]) if k=='P' and info[2]=='spent' else owner
                if not r.T.moves(mover,s): continue
                for other,otherkind,state in occ.get((c[0]+1,c[1],c[2]),()):
                    if other==owner: continue
                    if otherkind=='P' and state[2]=='spent' and r.carrier(other,state[0])==mover: continue
                    if other==mover and otherkind in ('g','RB'): continue
                    return 'sweep'
        for owner,base,direction in rod_targets(r):
            x,y,z=base
            target=(x+r.T.shift(owner,s),y+direction[0],z+direction[1])
            for delta in D6:
                if delta==(-1,0,0): continue
                for who,kind,info in occ.get(add(target,delta),()):
                    if kind=='P' and info[1]==0 and (info[2]=='spent' or who!=owner):
                        return 'rod powers foreign or spent piston'
    if power_problems(r): return 'power'
    for i,_,reason in r.check():
        if reason.startswith('disconnected') and driven_from_every_face(r,i): continue
        return reason
    return ''


def load(path):
    doc=json.loads(Path(path).read_text())
    data=[shape(*([tuple(x) for x in group] for group in m)) for m in doc['templates']]
    return data,doc['edges']


def close(path,pl,offsets,limit):
    data,edges=load(path)
    groups=defaultdict(list)
    for e in edges:
        if len(e['g'])+4+len(data[e['j']][1])<=pl: groups[e['i'],e['t']].append(e)
    counts=Counter()
    for length,screw in ((6,2),(12,1),(12,3)):
        for off in offsets:
            for i in range(len(data)):
                for a in groups[i,off[0]]:
                    for b in groups[a['j'],off[1]]:
                        for c in groups[b['j'],off[2]]:
                            if c['j']!=i: continue
                            r=candidate(data,[a,b,c],screw,length//3)
                            if not r: continue
                            why=first_issue(r); counts[why or 'accepted']+=1
                            if why: continue
                            target=HERE/f'ring_pl{pl}_{length}_{counts["accepted"]}.flyer'
                            save_flyer(r,pl,target)
                            target.with_suffix('.json').write_text(json.dumps(dict(templates=data,
                                edges=[a,b,c],sym=screw,length=length,loads=r.size())))
                            print(target, r.size(),flush=True)
                            if counts['accepted']>=limit: return
    print('Screen:',counts,flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('path')
    ap.add_argument('--pl',type=int,default=17)
    ap.add_argument('--limit',type=int,default=3)
    args=ap.parse_args()
    close(args.path,args.pl,[(-1,-1,0),(-2,0,0),(-2,-1,1),(-3,0,1)],args.limit)
