"""Shortest connector and material-seam substitutions for the verified N3 ring."""
from pathlib import Path
import csv,os,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from fastflyer import Block,Flyer,Kind
from flyers.WIP.astra_ringgen_safe import make

OUT=Path(__file__).resolve().parent/'n3_bridge'
RUNNER=Path(os.environ['TEMP'])/'flyer_measure.exe'
CENTERS=[(0,0),(0,4),(3,5),(5,2),(3,-1)]
DIRS=((1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))

def add(a,b):return tuple(a[i]+b[i] for i in range(3))
def dist(a,b):return sum(abs(a[i]-b[i]) for i in range(3))

def measure(f,ticks,path):
    f.save(path)
    p=subprocess.run([str(RUNNER),str(ticks),str(path)],capture_output=True,text=True)
    parts=p.stdout.strip().split('\t')
    return int(parts[1]) if p.returncode==0 and len(parts)>1 else -1

def main():
    OUT.mkdir(exist_ok=True)
    base,counts,(segments,_)=make(3,CENTERS,3,18)
    assert counts==[14,14,14,14,15]
    rear={(-2,-1,0),(-2,0,-1),(-2,0,0),(-2,1,0)}
    front={(2,3,-1),(2,2,-1),(2,4,-1),(2,3,-2)}
    assert rear|front<=segments[4]
    old=segments[4]-rear-front
    occupied=set(base._cells)-old
    minimum=min(dist(a,b) for a in rear for b in front)
    print('OLD',sorted(old),'minimum_distance',minimum,flush=True)
    routes=set()
    def walk(path,end,length):
        if len(path)-1==length:
            if path[-1]==end:
                cells=frozenset(path[1:-1])
                if not cells&occupied:routes.add(cells)
            return
        remaining=length-(len(path)-1)
        for d in DIRS:
            q=add(path[-1],d)
            if q in path or q in occupied and q!=end or dist(q,end)>remaining-1:continue
            walk(path+[q],end,length)
    for length in (minimum,minimum+2):
        for a in rear:
            for b in front:
                if dist(a,b)<=length:walk([a],b,length)
    routes=[x for x in routes if len(x)<len(old)]
    print('ROUTES',len(routes),flush=True)
    rows=[];started=time.monotonic()
    for ri,cells in enumerate(sorted(routes,key=lambda x:sorted(x))):
        for rotation in range(5):
            for invert in (0,1):
                kinds=[Kind.HONEY if (((i-rotation)%5)%2)^invert else Kind.SLIME for i in range(5)]
                f=Flyer(base.phase_x,base.phase_z,base.rng_state,18)
                f._cells={p:b for p,b in base._cells.items() if p not in old}
                for i,segment in enumerate(segments):
                    for p in segment-old:f.set(p,Block(kinds[i]))
                for p in cells:f.set(p,Block(kinds[4]))
                screen=OUT/'screen.flyer'
                d120=measure(f,120,screen)
                d1000=measure(f,1000,screen) if d120>=33 else -1
                d10000=measure(f,10000,screen) if d1000>=285 else -1
                rows.append((ri,len(cells),rotation,invert,d120,d1000,d10000))
                if d120>=33:
                    name=f'r{ri}_rot{rotation}_inv{invert}.flyer'
                    f.save(OUT/name)
                    print('LEAD',name,d120,d1000,d10000,flush=True)
        if time.monotonic()-started>120:break
    with (OUT/'summary.csv').open('w',newline='') as stream:
        w=csv.writer(stream);w.writerow(('route','connector_cells','seam_rotation','inverted','distance120','distance1000','distance10000'));w.writerows(rows)
    print('DONE',len(rows),'tests',round(time.monotonic()-started,1),'seconds',flush=True)

if __name__=='__main__':main()
