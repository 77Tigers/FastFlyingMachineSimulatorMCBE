"""Freeze the first mixed extension and test literal1/2/4/8 copy assemblies."""
from pathlib import Path
import sys,json,subprocess,importlib.util
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
HERE=Path(__file__).resolve().parent;RUNNER=ROOT/'target/release/fastflyer-research.exe'
spec=importlib.util.spec_from_file_location('model',HERE/'derived_mixed3_compact_v3.py');model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
def main():
    core=next(m for m in json.loads((HERE/'mixed3_compact_v3_manifest.json').read_text())['candidates'] if m['file']=='pentagon_wide_v1_s012.flyer')
    lead=next(m for m in json.loads((HERE/'mixed_extension_manifest.json').read_text())['candidates'] if m['file']=='dy12_dz0_s001.flyer')
    core_sets=[set(map(tuple,s)) for s in core['segments']];tile=[set(map(tuple,lead['segments'][i]))-core_sets[i] for i in range(5)]+[set(map(tuple,lead['segments'][5]))]
    bridged='--bridge' in sys.argv
    if bridged:
        bridge=json.loads((HERE/'mixed_tile_bridge.json').read_text())
        for i,cells in enumerate(bridge['connectors']):tile[i].update(map(tuple,cells))
    delta=lead['delta'];out=HERE/('mixed_tile_bridged' if bridged else 'mixed_tile_copies');out.mkdir(exist_ok=True);manifest=[]
    for copies in (1,2,4,8):
        ss=[s.copy() for s in core_sets];ps=list(core['pistons']);sources=list(core['sources'])
        def shift(p,k):return tuple(p[a]+k*delta[a] for a in range(3))
        for k in range(copies):
            newbody=len(ss);ss.append({shift(p,k) for p in tile[5]})
            for i in range(5):ss[i].update(shift(p,k) for p in tile[i])
            for p,dp,phase,target,sticky in lead['pistons'][-3:]:ps.append((shift(p,k),dp,phase,newbody,sticky))
            for p,owner,observer in lead['sources'][-3:]:sources.append((shift(p,k),newbody if owner==5 else owner,observer))
        connected=[len(model.conn(s))==len(s) for s in ss];f=Flyer(rng_state=5,push_limit=1000);kinds=model.K+[Kind.SLIME]*copies
        for p,owner,observer in sources:
            phase=owner if owner<5 else 0;f._cells[tuple(p)]=Block.observer(3,powered=bool(model.S[phase][4])) if observer else Block(Kind.REDSTONE_BLOCK)
        for p,dp,phase,target,sticky in ps:
            state=2 if (phase==0 if sticky else (0-phase)%5==1) else 0
            assert tuple(p) not in f._cells;f._cells[tuple(p)]=Block.piston(1 if sticky else 0,sticky=sticky,state=state)
            if state:f._cells[model.shift(p,-1 if sticky else 1)]=Block(Kind.PISTON_ARM)
        for i,s in enumerate(ss):
            for p in s:assert p not in f._cells;f._cells[p]=Block(kinds[i])
        path=out/f'copies{copies}.flyer';f.save(path)
        r=subprocess.run([str(RUNNER),'verify',str(path),'240','--period','10','--advance','3'],capture_output=True,text=True);path.with_suffix('.verify.txt').write_text(r.stdout+r.stderr);print(copies,connected,r.stdout,flush=True)
        manifest.append(dict(copies=copies,connected=connected,segments=[sorted(s) for s in ss],pistons=ps,sources=sources,counts=list(map(len,ss)),short_pass=r.returncode==0,result=r.stdout.strip()))
        (out/'manifest.json').write_text(json.dumps(dict(tile_segments=[sorted(s) for s in tile],translation=delta,assemblies=manifest),indent=2))
if __name__=='__main__':main()
