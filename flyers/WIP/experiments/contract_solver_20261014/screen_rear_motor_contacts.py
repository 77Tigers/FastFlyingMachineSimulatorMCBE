"""Necessary contact bounds for the calibrated rear push pair, not physics proof.

R wwmmm is pushed at2/3 by normals initially q-3X. The front mmwwm
carrier transports both at0/1 and recovers the first at4. Nominal actor
identities may exchange. Bounds allow all contact sides and ignore obstacles;
they exclude only this retained-front-glue/carrier allocation.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from assemble import Flyer

D=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
REAR={(13,3,11),(13,3,12),(13,4,12),(13,4,13),(13,4,14),(14,4,14),(15,4,14),(16,4,14)}
FRONT={(22,1,13),(22,2,13),(22,2,14),(22,3,13)}


def adj(p):
    return {tuple(a+b for a,b in zip(p,d)) for d in D}


def distance(a,b):
    return sum(abs(x-y) for x,y in zip(a,b))


def front_bound(root,front,rear_cap):
    # q belongs to a connected <=rear_cap rear scaffold rooted at root.
    # q-3X is adjacent to the front scaffold. A new front cell at distance k
    # from the retained connected front scaffold needs at least k added cells.
    shifted=(root[0]-3,*root[1:])
    separation=min(distance(shifted,h) for h in front)
    return separation,max(0,separation-(rear_cap-1)-1)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    f=Flyer.load(a.base/'problem.flyer')
    rows=[]
    for q1,q2 in itertools.combinations(sorted(REAR),2):
        def sources(q):
            return adj((q[0]-1,*q[1:]))-{q} # A piston cannot be powered from its front.
        for source in sorted(sources(q1)&sources(q2)):
            actors=[(q[0]-3,*q[1:]) for q in (q1,q2)]
            reasons=[]
            if source in f._cells:reasons.append('source occupied')
            if not adj(source)&REAR:reasons.append('source has no rear glue support')
            if any(p in f._cells for p in actors):reasons.append('normal initially occupied')
            if source in actors:reasons.append('source/normal overlap')
            lower=max(min(distance(p,h) for h in FRONT)-1 for p in actors)
            rows.append(dict(targets=[q1,q2],source=source,actors=actors,
                             minimum_added_front_glue_lower_bound=lower,rejections=reasons))
    separation,minimum=front_bound((13,3,11),FRONT,8)
    # Calibration: the independently and long-run accepted isolated push pair
    # has no extra-front-glue requirement when its existing bracket is retained.
    fixture_front={(12,0,11),(12,4,11),*((11,y,11) for y in range(5))}
    assert front_bound((15,2,11),fixture_front,3)==(1,0)
    assert (separation,minimum)==(14,6)
    # Exhaust all potentially reachable q in the obstacle-free radius7 ball.
    root=(13,3,11)
    reachable=[q for q in itertools.product(range(6,21),range(-4,11),range(4,19))
               if distance(q,root)<=7 and min(distance((q[0]-3,*q[1:]),h) for h in FRONT)<=5]
    assert not reachable
    report={'scope':__doc__,'base':str(a.base),'input_sha256':hashlib.sha256((a.base/'problem.flyer').read_bytes()).hexdigest(),
            'fixed_rear_shape':{'source_pair_count':len(rows),'initially_valid_count':sum(not r['rejections'] for r in rows),'pairs':rows},
            'joint_relaxed_bound':{'rear_root':root,'rear_glue_cap':8,'retained_front_glue':sorted(FRONT),
                                   'allowed_added_front_glue':4,'shifted_root_distance_to_front':separation,
                                   'necessary_added_front_glue_at_least':minimum,'reachable_target_count':len(reachable),
                                   'proof':'d(root-3X,old_front)<=rear_edges+normal_contact+new_front_cells; 14>7+1+4.',
                                   'excludes':'Retain all four current H0 glue cells, add at most four; same mmwwm/wwmmm actor allocation. Even rear glue may be fully reshaped.',
                                   'not_excluded':'Regenerate old H0 hardware/contacts, change carrier roles or power allocation, or change rear anchor/recovery geometry.'},
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'pairs':len(rows),'initially_valid':sum(not r['rejections'] for r in rows),'joint_minimum_front_additions':minimum,'budget':4}))


if __name__=='__main__':main()
