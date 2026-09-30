"""Map retained body geometry into the encoded file's normalized coordinates."""
from pathlib import Path
import sys,json,csv
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
def main():
    manifest=Path(sys.argv[1]);name=sys.argv[2];flyer=Path(sys.argv[3]);out=Path(sys.argv[4]);m=next(m for m in json.loads(manifest.read_text())['candidates'] if m['file']==name);f=Flyer.load(flyer)
    raw=[p for s in m['segments'] for p in s];actual=[p for p,b in f._cells.items() if b.kind in (Kind.SLIME,Kind.HONEY)];offset=[min(p[a] for p in actual)-min(p[a] for p in raw) for a in range(3)]
    phases=list(map(int,sys.argv[5].split(','))) if len(sys.argv)>5 else m.get('phases',[i%5 for i in range(len(m['segments']))]);assert len(phases)==len(m['segments'])
    with out.open('w',newline='') as stream:
        w=csv.writer(stream);w.writerow(['body','phase','x','y','z']);w.writerows((i,phases[i],*[p[a]+offset[a] for a in range(3)]) for i,s in enumerate(m['segments']) for p in s)
if __name__=='__main__':main()
