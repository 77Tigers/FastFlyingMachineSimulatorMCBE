"""Open backwards mv4 layers pulled by -X stickies; unchanged simulator.

Root uses the verified normal-piston driver. Each later bank has four sticky
members. Their extension phase is target+1, pull phase is target, recovery
carriers are self and the two phases AHEAD. No recovery dependency points back.
This is an experimental interface until actual simulation passes.
"""
import argparse, importlib.util, json, time
from pathlib import Path
import backward as w
r=w.r
spec=importlib.util.spec_from_file_location('sticky_builder',r.EXPERIMENTS/'mv4_redesign_20261004/builder.py')
b=importlib.util.module_from_spec(spec)
src=Path(spec.origin).read_text()
def replace(old,new):
    global src
    assert old in src,old
    src=src.replace(old,new)
replace("planes=[0]*N","planes=cfg.get('planes',[0]*N)\n bases=[planes[i]-1 if i<12 else planes[i]+2+disp((i%3+1)%3,i) for i in range(N)]")
replace("if any(following[i]%3!=(i+1)%3 or previous_carrier[i]%3!=(i+2)%3 for i in range(N)):",
        "if any(following[i]%3!=(i+(1 if i<12 else 2))%3 or previous_carrier[i]%3!=(i+(2 if i<12 else 1))%3 for i in range(N)):")
replace("def carrier(bank,rel):return (bank,following[bank],previous_carrier[bank])[rel]",
        "def carrier(bank,rel):return ((bank,following[bank],previous_carrier[bank]) if bank<12 else (previous_carrier[bank],following[bank],bank))[rel]")
replace("ph=bank%3;base=planes[bank]-1","ph=bank%3 if bank<12 else (bank%3+1)%3;base=bases[bank]")
replace("ss[bank].add(local(bank,1,y,z))","ss[bank].add(local(bank,1 if bank<12 else -2,y,z))")
replace("((bank,-1,own),(previous_carrier[bank],0,previous))",
        "((bank if bank<12 else previous_carrier[bank],-1,own),(previous_carrier[bank] if bank<12 else bank,0,previous))")
replace("bank=pspec['bank'];ph=bank%3","bank=pspec['bank'];ph=bank%3 if bank<12 else (bank%3+1)%3")
replace("planes[bank]-1+disp(t,bank)+x","bases[bank]+disp(t,ph)+x")
replace("if s in (1,2):fixedbad[i].add(shift(pp,1-dx))",
        "if s in (1,2):fixedbad[i].add(shift(pp,(1 if bank<12 else -1)-dx))")
replace("redundant=i==bank and shift(pp,1-dx) in ss[i]",
        "redundant=bank<12 and i==bank and shift(pp,1-dx) in ss[i]")
replace("refresh()\n for i,cells in enumerate(ss):","refresh()\n globals()['LAST_MANDATORY']=[set(v) for v in ss]\n for i,cells in enumerate(ss):")
replace("bounds=(-5,5,","bounds=(min(planes)-7,max(planes)+7,")
replace("owner=None if ophase is None else carrier(bank,(ophase-bank%3)%3)",
        "owner=None if ophase is None else carrier(bank,(ophase-(bank%3 if bank<12 else (bank%3+1)%3))%3)")
replace("Block.piston(0,state=s,moving=owner is not None)","Block.piston(0 if bank<12 else 1,sticky=bank>=12,state=s,moving=owner is not None)")
replace("if s in (1,2):flyer._cells[shift(q,1)]","if s in (1,2):flyer._cells[shift(q,1 if bank<12 else -1)]")
replace("if bank%3==2 and pspec['f']==11:","if bank%3==2 and pspec['f']==(11 if bank<12 else 9):")
src=src.replace('bank<12','bank<ROOT_BANKS').replace('bank>=12','bank>=ROOT_BANKS').replace('i<12','i<ROOT_BANKS')
exec(compile(src,spec.origin,'exec'),b.__dict__)
b.ROOT_BANKS=12


def configure(depth,pitch=10,radius=10,spacing=6):
    b.ROOT_BANKS=12
    n,cfg,placement=w.configure(depth,pitch,radius=radius,spacing=spacing)
    b.N=n;b.K=list(w.b.K)
    f=list(cfg['following'][:12]);p=list(cfg['previous_carrier'][:12])
    for layer in range(1,depth+1):
        for j in range(12):
            f.append((layer-1)*12+(j-1+3)%12) # source/ribbon: target+2
            p.append((layer-1)*12+(j+1+3)%12) # other pickup: target+1
    cfg=cfg|dict(following=f,previous_carrier=p)
    return n,cfg,placement


def build_all_sticky(seconds=120,seed=0,radius=10,spacing=6):
    _,_,large=w.configure(1,10,radius=radius,spacing=spacing)
    n=12;b.N=n;b.K=[b.Kind.SLIME if i%2==0 else b.Kind.HONEY for i in range(n)]
    w.b.N=n;w.b.K=list(b.K);b.ROOT_BANKS=0
    cfg=w.BASE['config'] | dict(following=[(j-1)%12 for j in range(12)],
        previous_carrier=[(j+1)%12 for j in range(12)])
    placement=(large[0][12:],large[1][12:],large[2][12:]);report={}
    def route(must,fixed,bounds,cap,rng):
        report['mandatory']=list(map(len,must))
        return w.route(must,fixed,bounds,cap,rng,time.monotonic()+seconds,report)
    ans,why=b.build(seed,placement,cap=400,joint_router=route,config=cfg)
    return ans,dict(all_sticky=True,radius=radius,spacing=spacing,seed=seed,rejection=why,**report)


def build(depth=2,pitch=10,seconds=90,seed=0,radius=10,spacing=6):
    n,cfg,placement=configure(depth,pitch,radius,spacing);report={}
    def route(must,fixed,bounds,cap,rng):
        report['mandatory']=list(map(len,must))
        return w.route(must,fixed,bounds,cap,rng,time.monotonic()+seconds,report)
    ans,why=b.build(seed,placement,cap=400,joint_router=route,config=cfg)
    return ans,dict(depth=depth,pitch=pitch,radius=radius,spacing=spacing,seed=seed,rejection=why,**report)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--depth',type=int,default=2)
    parser.add_argument('--seconds',type=int,default=120);parser.add_argument('--pitch',type=int,default=10)
    parser.add_argument('--seed',type=int,default=0)
    parser.add_argument('--all-sticky',action='store_true');args=parser.parse_args()
    ans,report=(build_all_sticky(args.seconds,args.seed) if args.all_sticky
                else build(args.depth,args.pitch,args.seconds,args.seed))
    if ans:
        name='all_sticky' if args.all_sticky else 'sticky_prototype'
        f,m=ans;f.push_limit=160 if args.all_sticky else 256;f.save(r.HERE/(name+'.flyer'))
        m.update(depth=0 if args.all_sticky else args.depth,pitch=args.pitch,all_sticky=args.all_sticky)
        (r.HERE/(name+'.json')).write_text(json.dumps(m,indent=2))
        report.update(routed=True,counts=m['counts'])
    path=r.HERE/'sticky_status.json'
    old=json.loads(path.read_text()) if path.exists() else []
    old.append(report);path.write_text(json.dumps(old,indent=2))
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
