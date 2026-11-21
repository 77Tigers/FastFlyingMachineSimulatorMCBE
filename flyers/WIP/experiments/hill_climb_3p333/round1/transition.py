"""Try one staggered two-pair body between a flat + and the next flat module."""
from probe import *
from stagger import modules


def step(args):
    src,dst,i,j,t,pl=args
    _,es=row((i,src,[dst],[t],pl,5))
    for e in es: e['j']=j
    return es


def main(pl,jobs):
    import flexible
    cuts=native_library().pose
    cuts.argtypes=flexible.native.argtypes
    flexible.native=cuts
    doc=json.loads((HERE/'flex_links.json').read_text())
    flat=cores('compact')
    data=flat+modules(3)
    plus_id=next(i for i,(_,r,_) in enumerate(flat) if len(r)==1)
    edges=[e for e in doc['edges'] if e['j']==plus_id and e['t']>=0 and
           len(e['g'])+5<=pl]
    jobs1=[(data[plus_id],w,plus_id,j,t,pl) for t in (-2,-1,-3,0,-4)
           for j,w in enumerate(data) if j>=len(flat)]
    with ProcessPoolExecutor(jobs) as ex:
        for es in ex.map(step,jobs1):
            edges.extend(es)
    mid={(e['j'],e['t']) for e in edges if e['i']==plus_id and e['j']>=len(flat)}
    print('middle options',Counter(t for _,t in mid),flush=True)
    need={(j,a['i'],-2-t-a['t']) for j,t in mid for a in edges if a['j']==plus_id and a['t']>=0}
    jobs2=[(data[i],data[j],i,j,t,pl) for i,j,t in sorted(need)]
    with ProcessPoolExecutor(jobs) as ex:
        for es in ex.map(step,jobs2): edges.extend(es)
    path=HERE/'transitions.json'
    path.write_text(json.dumps(dict(templates=data,edges=edges)))
    offsets=sorted({(a['t'],t,-2-t-a['t']) for _,t in mid for a in edges if a['j']==plus_id and a['t']>=0})
    close(path,pl,offsets,1)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--jobs',type=int,default=8);p.add_argument('--pl',type=int,default=17)
    args=p.parse_args(); main(args.pl,args.jobs)
