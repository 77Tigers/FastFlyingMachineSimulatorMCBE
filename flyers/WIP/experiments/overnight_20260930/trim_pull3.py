"""Reduce connected adhesive geometry of the first exact pulling-only3bps lead."""
from pathlib import Path
import sys,subprocess,json,random,re
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
from pull3_synthesis import conn
HERE=Path(__file__).resolve().parent;RUNNER=ROOT/'flyers/WIP/experiments/bin/research_runner.exe'
def main():
    m=next(m for m in json.loads((HERE/'pull3_10body_manifest.json').read_text())['candidates'] if m['spacing']==4 and m['seed']==3)
    f=Flyer.load(HERE/'pull3_10body_candidates/g4_s003.flyer');f.push_limit=1000
    raw=[tuple(p) for s in m['segments'] for p in s]
    actual=[p for p,b in f._cells.items() if b.kind in (Kind.SLIME,Kind.HONEY)]
    offset=tuple(min(p[a] for p in actual)-min(p[a] for p in raw) for a in range(3))
    segments=[{tuple(p[a]+offset[a] for a in range(3)) for p in s} for s in m['segments']]
    assert set.union(*segments)==set(actual)
    out=HERE/'trim_pull3';out.mkdir(exist_ok=True);log=[]
    for cycle in range(5):
        removed=0;sites=[(i,p) for i,s in enumerate(segments) for p in s];random.Random(40+cycle).shuffle(sites)
        for i,p in sites:
            if conn(segments[i]-{p})!=segments[i]-{p}:continue
            b=f._cells.pop(p);probe=out/'probe.flyer';f.save(probe)
            r=subprocess.run([str(RUNNER),'verify',str(probe),'160','--period','10','--advance','3'],capture_output=True,text=True)
            ok=r.returncode==0;log.append(dict(cycle=cycle,position=p,body=i,accepted=ok,result=r.stdout.strip()))
            if ok:segments[i].remove(p);removed+=1;f.save(out/'best.flyer')
            else:f._cells[p]=b
            (out/'results.pending.json').write_text(json.dumps(log,indent=2));(out/'results.pending.json').replace(out/'results.json')
        print('pull3 trim',cycle,'removed',removed,'sticky',list(map(len,segments)),flush=True)
        if not removed:break
    f.save(out/'best.flyer')
    r=subprocess.run([str(RUNNER),'verify',str(out/'best.flyer'),'10000','--period','10','--advance','3'],capture_output=True,text=True)
    (out/'diagnostic_full.txt').write_text(r.stdout+r.stderr);assert r.returncode==0
    f.push_limit=int(re.search(r'max_successful_action=(\d+)',r.stdout)[1]);path=HERE/f'pull3_trim_pl{f.push_limit}.flyer';f.save(path)
    (out/'geometry.json').write_text(json.dumps(dict(segments=[sorted(s) for s in segments],source_metadata=m,source_offset=offset),indent=2))
    for name,args in [('verify',[str(path),'10000','--period','10','--advance','3']),('audit',[str(path),'10000','10']),('samples',[str(path),'--period','10','--advance','3','--out',str(path.with_suffix('.samples.csv'))])]:
        r=subprocess.run([str(RUNNER),name,*args],capture_output=True,text=True)
        path.with_suffix('.'+name+'.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True);assert r.returncode==0
if __name__=='__main__':main()
