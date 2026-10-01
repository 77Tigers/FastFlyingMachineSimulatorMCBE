"""Bounded new family: one all-pull body, remaining all-push bodies.
Reuse read-only A/B routing tools, but allow ANY resting carrier as anchor.
Never serialize or simulate a design above PL24. Static rejections are not proofs.
"""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'ab_20261001'))
import abpr
from abgen_g import Lay2
from abworld import World
from abcheck import check

def lifecycle(lay):
    out = []
    for b in lay.bodies:
        for s in range(lay.L):
            if not lay.moves(b, s): continue
            kind = 'Q' if b == lay.bodies[0] else 'P'
            f = (s-1) % lay.L if kind == 'Q' else s
            p = dict(kind=kind,s=s,f=f,victim=b,
                     anchors=[a for a in lay.bodies if a != b and not lay.moves(a,s)])
            p['xrel'] = [0]
            for j in range(lay.L):
                p['xrel'].append(p['xrel'][-1] + int((f+j)%lay.L not in (f,(f+1)%lay.L)))
            out.append(p)
    return out

def main(n, count):
    L=n+2
    words=[''.join('m' if (t-i)%L<n else 'w' for t in range(L)) for i in range(L)]
    lay=Lay2(words[:1],words)
    abpr.lifecycle=lifecycle
    cols=abpr.valid_colorings(lay)
    print('n',n,'words',words,'colorings',len(cols),flush=True)
    out=HERE / ('mixed_n'+str(n));out.mkdir(exist_ok=True)
    with (out/'results.jsonl').open('w') as log:
        for seed in range(count):
            if not cols: break
            glue=cols[seed%len(cols)]
            inc,err=abpr.place_route(lay,seed,glue,npos=16,nopt=24,keep=12,win=2,stack=1)
            rec={'seed':seed,'error':err}
            if inc is not None:
                load=abpr.est_load(inc); rec['estimated_load']=load
                if load<=24:
                    wd=World(lay,inc.req,inc.pist,inc.sources,glue=glue)
                    problems=check(wd);rec['problems']=len(problems)
                    if not problems:
                        wd.flyer(limit=24).save(out/f's{seed:04d}.flyer')
            line=json.dumps(rec);log.write(line+'\n');log.flush();print(line,flush=True)

if __name__=='__main__':main(int(sys.argv[1]),int(sys.argv[2]))

