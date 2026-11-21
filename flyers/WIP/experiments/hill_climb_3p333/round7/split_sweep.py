"""Enumerate complete cross-half X assignments and join their local 3D poses."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess

from itertools import product
from handoffs import HERE, NAMES
from second_pull import STENCILS


def allocations():
    result=[]
    for a,name in enumerate(NAMES):
        hs,_,gs=STENCILS[name]
        for owners in product(range(2),repeat=len(gs)):
            masks=tuple(sum(1<<i for i,v in enumerate(owners) if side==v) for side in range(2))
            choices=[{o for g,o in zip(gs,owners) if abs(h[0]-g[0])+abs(h[1]-g[1])==1} for h in hs]
            # A carrier moving first picks up every spent piston adjacent
            # to its cover. The middle T3 piston charges both split carriers.
            result.append((a,*masks,sum(0 in c for c in choices),sum(1 in c for c in choices)))
    return sorted(set(result))


def matrix():
    def run(args):
        raw=subprocess.check_output([HERE/'links',*map(str,args),'open'],text=True)
        return [tuple(map(int,line.split()[:5])) for line in raw.splitlines()]
    with ThreadPoolExecutor(6) as pool:
        return [row for group in pool.map(run,product(range(3),range(3),range(5,15))) for row in group]


def sweep(folder):
    programs=folder/'offsets.txt'
    atlas=folder/'relative.txt'
    survivors=folder/'survivors.txt'
    options=allocations()
    data=str(len(options))+'\n'+'\n'.join(' '.join(map(str,row)) for row in options+matrix())+'\n'
    with programs.open('w') as out:
        p=subprocess.run([HERE/'offsets'],input=data,text=True,stdout=out,stderr=subprocess.PIPE,check=True)
    print(p.stderr.strip(),flush=True)
    keys=set()
    for line in programs.open():
        row=list(map(int,line.split()))
        for i in range(6):
            for side in range(2):
                mask=row[18+2*i+side]
                if mask:
                    j=(i+1)%3+3*side
                    keys.add((row[i],row[j],row[12+j],mask,row[6+j]-row[6+i]-2*(i%3==2)))
    def poses(key):
        raw=subprocess.check_output([HERE/'links','poses',*map(str,key)],text=True)
        return ' '.join(map(str,(*key,len(raw.splitlines()))))+'\n'+raw
    with ThreadPoolExecutor(6) as pool, atlas.open('w') as out:
        out.writelines(pool.map(poses,sorted(keys)))
    with survivors.open('w') as out:
        q=subprocess.run([HERE/'world',atlas,programs],text=True,stdout=out,stderr=subprocess.PIPE,check=True)
    print(q.stderr.strip(),flush=True)
    return p.stderr.strip(),q.stderr.strip(),survivors


if __name__=='__main__':
    import tempfile
    with tempfile.TemporaryDirectory(dir=HERE) as directory:
        a,b,path=sweep(Path(directory))
        for row in path.read_text().splitlines()[:1]: print(row)
