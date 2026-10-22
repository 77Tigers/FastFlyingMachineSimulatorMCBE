"""Bounded joint T/G cross-section templates, strict encoded11 evaluation.

Five/six T glue cells, selectable G body budget; tip supplied.
Optional neighbor-carried observer powers the rear pull independently of G sources.
All glue identities get motion ports; no hardware library/reference input.
"""
import os as _research_os
import argparse,itertools,json,subprocess,time
from pathlib import Path
from assemble import Flyer,ROOT,port_pos
from fastflyer import Block

D=((1,0),(-1,0),(0,1),(0,-1))
def near(p):return {(p[0]+a,p[1]+b) for a,b in D}
def dist(a,b):return abs(a[0]-b[0])+abs(a[1]-b[1])
def connected(s):
    seen={next(iter(s))}
    while True:
        new=seen|set.union(*(near(p)&s for p in seen))
        if new==seen:return seen==s
        seen=new
def direction(a,b):return {(1,0):2,(-1,0):3,(0,1):4,(0,-1):5}[(b[0]-a[0],b[1]-a[1])]

def layouts(front_core=3, helper_body=10, neighbor_power=False):
    r=(0,0)
    for t1,t2 in itertools.permutations(D,2):
        seed={r,t1,t2}
        cores={frozenset(seed)}
        for _ in range(front_core-3):
            cores={frozenset(set(c)|{p}) for c in cores for p in set.union(*(near(q) for q in c))-set(c)}
        for core in sorted(cores,key=lambda c:sorted(c)):
            tc=set(core)
            boundary=set.union(*(near(p) for p in tc))-tc
            for ot in sorted(tc):
                for q0 in sorted(near(ot)&tc):
                    for l1,l2 in itertools.combinations(sorted(boundary),2):
                        singles=[(s,) for s in sorted(near(l1)&near(l2)-tc-{q0})]
                        duals=[(s1,s2) for s1 in sorted(near(l1)-tc-{q0,l2}) for s2 in sorted(near(l2)-tc-{q0,l1,s1})]
                        for sources in singles+duals:
                            q1s=(near(t1)&boundary)-{l1,l2}
                            q1s={q for q in q1s if neighbor_power or any(dist(q,s)==1 for s in sources)}
                            if not q1s:continue
                            needed={l1,l2,*sources}
                            maxbase=helper_body-4-len(sources)
                            options={frozenset(needed)}
                            for n in range(len(needed),maxbase+1):
                                for gs in sorted(options,key=lambda s:sorted(s)):
                                    if q0 in gs or ot in gs or not connected(set(gs)) or not near(q0)&gs:continue
                                    for og in sorted(gs):
                                        for qh in sorted(gs-{og}):
                                            for ht in sorted(near(og)&near(qh)):
                                                for q1 in sorted(q1s):
                                                    for un in sorted(near(t2)-{q1}):
                                                        if dist(un,q1)<=1:continue
                                                        powers=sorted((near(un)&near(q1))-tc-boundary) if neighbor_power else [None]
                                                        for power in powers:
                                                            yield tc,t1,t2,ot,q0,l1,l2,sources,set(gs),og,qh,ht,q1,un,power
                                if n<maxbase:
                                    options={frozenset(set(s)|{p}) for s in options for p in set.union(*(near(p) for p in s))-set(s)-{q0,ot}}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("output",type=Path);ap.add_argument("--seconds",type=float,default=240);ap.add_argument("--cases",type=int,default=2000);ap.add_argument("--front-core",type=int,choices=(3,4),default=3);ap.add_argument("--helper-body",type=int,choices=(8,9,10),default=10);ap.add_argument("--neighbor-front-power",action="store_true");ap.add_argument("--continue-after-lead",action="store_true");ap.add_argument("--exact-helper-body",action="store_true");a=ap.parse_args()
    if a.output.exists():raise ValueError("existing search")
    a.output.mkdir(parents=True);start=time.monotonic();state={"complete":False,"tested":0,"cases":[],"front_core":a.front_core,"helper_body_cap":a.helper_body,"neighbor_front_power":a.neighbor_front_power,"neighbor_power_kind":"observer" if a.neighbor_front_power else None};seen=set()
    save=lambda:(a.output/"summary.json").write_text(json.dumps(state,indent=2)+"\n")
    for config in layouts(a.front_core,a.helper_body,a.neighbor_front_power):
        if time.monotonic()-start>=a.seconds or state['tested']>=a.cases:break
        tc,t1,t2,ot,q0,l1,l2,sources,gs,og,qh,ht,q1,un,power=config
        if a.exact_helper_body and len(gs)+len(sources)+4 != a.helper_body:continue
        f=Flyer(push_limit=11);cells={};bad=False
        def put(x,p,b):
            nonlocal bad
            at=(x,*p)
            if at in cells:bad=True
            cells[at]=b
        tg=[(17,*p) for p in sorted(tc)]+[(18,*ot),(19,*ot)]
        gg=[(19,*p) for p in sorted(gs)]+[(20,*og),(21,*og)]
        for p in tg:put(p[0],p[1:],Block.decode(1))
        for p in gg:put(p[0],p[1:],Block.decode(2))
        for x,p,b in [(16,(0,0),Block.decode(6)),(14,t1,Block.piston(0)),(15,t2,Block.piston(0,state=2)),(16,t2,Block.decode(10)),(14,q1,Block.decode(2)),(14,un,Block.decode(2)),(17,q1,Block.piston(1,sticky=True)),(19,q0,Block.piston(1,sticky=True,state=2)),(18,q0,Block.decode(10)),(20,ot,Block.observer(direction(ot,q0),powered=True)),(17,l1,Block.piston(0)),(17,l2,Block.piston(0)),(21,ht,Block.decode(1)),(21,qh,Block.piston(1,sticky=True)),(22,og,Block.observer(direction(og,ht)))]:put(x,p,b)
        for s in sources:put(18,s,Block.decode(6))
        if power is not None:
            for x in (15,16,17):put(x,un,Block.decode(2))
            put(17,power,Block.observer(direction(power,q1)))
        if bad:continue
        signature=tuple(sorted((p,b.encode()) for p,b in cells.items()))
        if signature in seen:continue
        seen.add(signature)
        for p,b in cells.items():f.set(p,b)
        out=a.output/f"case{state['tested']:05d}";out.mkdir();f.save(out/'problem.flyer');g=Flyer.load(out/'problem.flyer')
        minimum=lambda cs:tuple(min(p[k] for p in cs) for k in range(3))
        delta=tuple(b-a for a,b in zip(minimum(f._cells),minimum(g._cells)));sh=lambda p:[v+d for v,d in zip(p,delta)]
        if {tuple(sh(p)):b.encode() for p,b in f._cells.items()}!={p:b.encode() for p,b in g._cells.items()}:raise ValueError("normalization")
        ports=[{"name":f"T{i}","at":sh(p),"word":"mwwmm","role":"output"} for i,p in enumerate(tg)]+[{"name":f"G{i}","at":sh(p),"word":"wmmmw","role":"output"} for i,p in enumerate(gg)]
        ports += [{"name":n,"at":sh((x,*p)),"word":w,"role":"input"} for n,x,p,w in [('back',14,q1,'mmmww'),('neighbor',14,un,'mmmww'),('tip',21,ht,'mmwwm')]]
        if power is not None:
            ports += [{"name":f"neighbor_support{x}","at":sh((x,*un)),"word":"mmmww","role":"input"} for x in (15,16,17)]
        drive=[(t,*port_pos(p,t,10,3),11) for p in ports if p['role']=='input' and not p['name'].startswith('neighbor_support') for t in range(30) if t%2==0 and p['word'][(t%10)//2]=='m' and not(p['name']=='back' and t%10==4)]
        c={"version":1,"name":"joint_tip_layout","flyer":"problem.flyer","prescribed_script":"drive.txt","prescribed_order":"before_natural","period_ticks":10,"advance":3,"cycles":3,"recurrence":"bounded","ports":ports,"required_cells":[{"at":list(p),"cell":b.encode()} for p,b in g._cells.items() if b.kind!=10],"boundary_envelope":{"min":[min(p[k] for p in g._cells)-5 for k in range(3)],"max":[max(p[k] for p in g._cells)+5 for k in range(3)]}}
        (out/'problem.json').write_text(json.dumps(c,indent=2)+'\n');(out/'drive.txt').write_text('\n'.join(' '.join(map(str,r)) for r in sorted(drive))+'\n')
        subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(out/'problem.json'),str(out/'result.json'),'10','4'],capture_output=True,text=True)
        report=json.loads((out/'result.json').read_text());state['cases'].append({"case":out.name,**report});state['tested']+=1;save()
        if report['verified']:
            state.setdefault('leads',[]).append(str(out));state['lead']=str(out)
            if not a.continue_after_lead:break
    else:state['complete']=True
    state['elapsed_seconds']=time.monotonic()-start;save();print(json.dumps({k:v for k,v in state.items() if k!='cases'}))

if __name__=='__main__':main()
