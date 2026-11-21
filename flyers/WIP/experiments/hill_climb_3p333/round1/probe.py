"""Search heterogeneous three-link cycles, beginning with the expensive zero-offset edge."""
from flexible import *
import flexible
from close import close


def rows(args):
    i,v,targets,t,data,pl=args
    es=[]
    for j in targets:
        _,edges=row((i,v,[data[j]],[t],pl,5))
        for e in edges: e['j']=j
        es.extend(edges)
    return i,es


def run(data,pl,jobs,name):
    all_edges=[]
    # For a cycle A -(0)-> B -(-1)-> C -(-1)-> A, isolate A and B
    # after the first pass so the next two scans skip irrelevant shapes.
    A=B=C=set(range(len(data)))
    for round_id in range(3):
        if round_id==0: pairs=[(i,A) for i in A]; t=0
        if round_id==1:
            A={e['i'] for e in all_edges};B={e['j'] for e in all_edges}
            pairs=[(i,C) for i in B];t=-1
        if round_id==2:
            C={e['j'] for e in all_edges if e['t']==-1}
            pairs=[(i,A) for i in C];t=-1
        if not pairs: break
        with ProcessPoolExecutor(jobs) as ex:
            tasks=[(i,data[i],sorted(ends),t,data,pl) for i,ends in pairs]
            for i,edges in ex.map(rows,tasks):
                all_edges.extend(edges)
                if edges: print(round_id,i,len(edges),flush=True)
        path=HERE/f'{name}.json'
        path.write_text(json.dumps(dict(templates=data,edges=all_edges)))
        if round_id==2: close(path,pl,[(-1,-1,0)],1)


if __name__=='__main__':
    import stagger
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',default='small')
    ap.add_argument('--jobs',type=int,default=5)
    ap.add_argument('--pl',type=int,default=17)
    args=ap.parse_args()
    new=native_library().pose
    new.argtypes=flexible.native.argtypes
    flexible.native=new
    data=cores(args.mode)
    print('cores',len(data),flush=True)
    run(data,args.pl,args.jobs,'flex_'+args.mode)
