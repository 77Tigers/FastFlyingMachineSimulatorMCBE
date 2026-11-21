"""Take the lowest-load six-body flat ring that passes the all-slot geometry check."""
from close import *


def minimum(path,pl=18):
    data,es=load(path)
    groups=defaultdict(list)
    for e in es: groups[e['i'],e['t']].append(e)
    def cost(e): return len(e['g'])+len(data[e['j']][1])+4
    opts=[]
    for i in range(len(data)):
        for a in groups[i,-1]:
            for b in groups[a['j'],-1]:
                for c in groups[b['j'],0]:
                    if c['j']==i and max(map(cost,(a,b,c)))<=pl:
                        opts.append((sum(map(cost,(a,b,c))),a,b,c))
    opts.sort(key=lambda x:x[0])
    for score,a,b,c in opts:
        r=candidate(data,[a,b,c],2,2)
        if not r or first_issue(r): continue
        target=HERE/f'screw6_pl{pl}.flyer'
        r.flyer(pl).save(str(target))
        target.with_suffix('.json').write_text(json.dumps(dict(templates=data,edges=[a,b,c],sym=2,length=6,loads=r.size())))
        print(target,score,r.size()); return


def rebuild():
    path=HERE/'screw6_pl18.json'
    data,edges=load(path)
    ring=candidate(data,edges,2,2)
    assert ring and not first_issue(ring)
    assert ring.size()==[14,13,13,14,13,13]
    save_flyer(ring,18,path.with_suffix('.flyer'))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--search',action='store_true')
    if parser.parse_args().search: minimum(HERE/'control_links.json')
    else: rebuild()
