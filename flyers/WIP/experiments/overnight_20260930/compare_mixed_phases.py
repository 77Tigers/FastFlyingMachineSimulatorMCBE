"""Locate the first discrepancy against the declared member/body trajectories."""
from pathlib import Path
import sys,json,csv,collections
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
HERE=Path(__file__).resolve().parent
S=[[(t+p)%5<3 for t in range(5)] for p in range(5)];DISP=[[sum(s[:t]) for t in range(5)] for s in S];K=[Kind.SLIME,Kind.HONEY,Kind.SLIME,Kind.HONEY,Kind.SLIME]
def main():
    m=next(m for m in json.loads((HERE/'mixed3_compact_manifest.json').read_text())['candidates'] if m['file']=='pentagon_v0_s010.flyer')
    f=Flyer.load(HERE/'mixed3_compact_candidates'/m['file']);raw=[tuple(p) for s in m['segments'] for p in s];actual=[p for p,b in f._cells.items() if b.kind in K]
    offset=tuple(min(p[a] for p in actual)-min(p[a] for p in raw) for a in range(3))
    worlds=collections.defaultdict(dict)
    for r in csv.DictReader((HERE/'mixed3_pentagon_s010_snapshots.csv').open(encoding='utf-8-sig')):worlds[int(r['tick'])][tuple(int(r[k]) for k in ('x','y','z'))]=Block.decode(int(r['cell']))
    output=[]
    for tick,world in worlds.items():
        slot=(tick//2)%5;cycle=tick//10;expected={};tags={}
        def put(p,dx,b,tag):
            q=(p[0]+dx+offset[0],p[1]+offset[1],p[2]+offset[2]);expected[q]=b;tags[q]=tag
        for i,s in enumerate(m['segments']):
            for p in s:put(p,cycle*3+DISP[i][slot],Block(K[i]),'body'+str(i))
        for p,owner,observer in m['sources']:put(p,cycle*3+DISP[owner][slot],Block.observer(5,powered=bool(S[owner][(slot-1)%5])) if observer else Block(Kind.REDSTONE_BLOCK),'source'+str(owner))
        for n,(p,dp,phase,target,sticky) in enumerate(m['pistons']):
            state=2 if (slot==phase if sticky else (slot-phase)%5==1) else 0
            put(p,cycle*3+dp[slot],Block.piston(1 if sticky else 0,sticky=sticky,state=state),'piston'+str(n))
            if state:put((p[0]+(-1 if sticky else 1),p[1],p[2]),cycle*3+dp[slot],Block(Kind.PISTON_ARM),'arm'+str(n))
        # Angry bits are diagnosed separately; masking them is not a bank gate.
        differences=[]
        for p in sorted(set(expected)|set(world)):
            e=expected.get(p);a=world.get(p)
            if (e.encode() if e else 0)!=(a.encode()&~512 if a else 0):differences.append(dict(position=p,tag=tags.get(p),expected=str(e),actual=str(a)))
        if differences:output.append(dict(tick=tick,difference_count=len(differences),differences=differences[:24]))
    assert not output or output[0]['tick']!=0,'initial metadata mismatch'
    (HERE/'mixed3_pentagon_s010_phase_diff.json').write_text(json.dumps(output,indent=2));print(json.dumps(output[:2],indent=2))
if __name__=='__main__':main()
