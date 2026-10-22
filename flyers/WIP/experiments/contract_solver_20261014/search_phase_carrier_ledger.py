"""Bounded whole39-stroke carrier/contact allocation, without spatial layout.

Uses the existing layered trajectory/contact hazard rules, fixed complete
hardware masses and optionally G0 third4. Permits front carriers to take
rear passengers. A passing ledger is a necessary role hypothesis, never a
flyer or proof that its source, glue, relay or recovery geometry can be built.
"""
import argparse,hashlib,importlib.util,json
from pathlib import Path
from ortools.sat.python import cp_model

HERE=Path(__file__).resolve().parent
ROLE=HERE.parent/'tm_smol_rebalance_20261001/j2_front_smol/layered.py'


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    ap.add_argument('--seconds',type=float,default=45);ap.add_argument('--original-G0',action='store_true')
    ap.add_argument('--cap',type=int,default=12)
    ap.add_argument('--current-component',action='store_true',help='Calibration: current hardware/words with two rear pushes still supplied')
    ap.add_argument('--relay-carrier',choices=['T0','T1','G0','H2_power'],default='T0')
    ap.add_argument('--front-glue-reserve',type=int,default=4)
    ap.add_argument('--mass-delta',action='append',default=[],metavar='BODY=DELTA',help='Explicit hardware or glue budget change before role allocation')
    ap.add_argument('--carry',action='append',default=[],metavar='TARGET:SLOT:BODY:SLOTS',help='Require actual component carrier pickups on specified period slots')
    ap.add_argument('--action-kind',action='append',default=[],metavar='TARGET:SLOT:push|pull',help='Explicit architecture change before computing piston trajectories and carrier budgets')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('role_rules',ROLE);role=importlib.util.module_from_spec(spec);spec.loader.exec_module(role)
    contract=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'));audit=json.loads((a.base/'failure_audit_0_0_7.json').read_text(encoding='utf-8'))
    words={p['name']:p['word'] for p in contract['ports']};positions={p['name']:p['at'] for p in contract['ports']};mass={};kinds={}
    for action in audit['actions']:
        if action['tick']>=10:continue
        body=action['moved_ports'][0];slot=action['tick']//2
        fixed={tuple(i[4]) for i in action['identities'] if i[3]&15!=9}
        if body in mass:assert mass[body]==len(fixed)
        mass[body]=len(fixed);kinds[body,slot]='pull' if action['action']=='retract' else 'push'
    if not a.original_G0 and not a.current_component:
        words['G0']='wmmwm';kinds.pop(('G0',3));kinds['G0',4]='push'
    if a.current_component:
        kinds.pop(('rear_pickup',2));kinds.pop(('rear_pickup',3))
    else:
        mass[a.relay_carrier]+=1 # T0 baseline RB removed, observer added: net0; explicit stone rider
        mass['rear_pickup']+=1 # new rear push-pair RB
        mass['H0']+=a.front_glue_reserve # explicit front contact-geometry reserve
    changes={}
    for value in a.mass_delta:
        body,delta=value.split('=',1);assert body in mass;changes[body]=changes.get(body,0)+int(delta)
    for body,delta in changes.items():mass[body]+=delta;assert mass[body]>=0
    action_changes={}
    for value in a.action_kind:
        body,slot,kind=value.split(':');slot=int(slot)
        assert (body,slot) in kinds and kind in ('push','pull'),value
        action_changes[f'{body}:{slot}']={'before':kinds[body,slot],'after':kind};kinds[body,slot]=kind
    mv={b:role.moves(w) for b,w in words.items()}
    # Regression of the failed direct same-word late-normal handoff.
    tr=role.trajectory(role.moves('mwwmm'),'push',4)
    assert not any(bits[3] for bits in role.options(role.moves('mwwmm'),role.moves('wmmmw'),False,'push',*tr[:2],*tr[2:]))
    model=cp_model.CpModel();terms={(b,t):[] for b,w in mv.items() for t,m in enumerate(w) if m};cost=[];records=[];empty=[]
    for (target,slot),kind in sorted(kinds.items()):
        trajectory=role.trajectory(mv[target],kind,slot)
        if trajectory is None:empty.append((target,slot,kind));continue
        firing,frozen,pm,rel=trajectory;coverage={t:[] for t in range(5) if pm[t]};choices=[]
        for carrier,word in mv.items():
            options=role.options(mv[target],word,carrier==target,kind,firing,frozen,pm,rel)
            if not options:empty.append((target,slot,kind,carrier));continue
            vs=[]
            for oi,bits in enumerate(options):
                v=model.NewBoolVar(f'{target}_{slot}_{carrier}_{oi}');vs.append(v)
                active=[t for t in range(5) if pm[t] and word[t] and bits[t]]
                for t in active:coverage[t].append(v);terms[carrier,t].append(v)
                dist=sum(abs(x-y) for x,y in zip(positions[target],positions[carrier]))
                cost.append((100+dist if active else 0)*v)
                choices.append((carrier,bits,active,v))
            model.AddExactlyOne(vs)
        for t,vs in coverage.items():model.Add(sum(vs)>=1)
        records.append({'target':target,'slot':slot,'kind':kind,'firing':firing,'frozen':sorted(frozen),'piston_word':''.join('m' if p else 'w' for p in pm),'relative':rel,'choices':choices})
    for requirement in a.carry:
        target,slot,body,slots=requirement.split(':');row=next(r for r in records if r['target']==target and r['slot']==int(slot))
        for t in map(int,slots):model.Add(sum(v for b,bits,active,v in row['choices'] if b==body and t in active)>=1)
    if empty:model.Add(0==1)
    peak=model.NewIntVar(0,30,'peak')
    for (body,slot),vs in terms.items():model.Add(mass[body]+sum(vs)<=a.cap);model.Add(peak>=mass[body]+sum(vs))
    model.Minimize(10000*peak+sum(cost));solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=a.seconds;solver.parameters.num_search_workers=2
    status=solver.Solve(model);report={'scope':__doc__,'status':solver.StatusName(status),'seconds':solver.WallTime(),'cap':a.cap,'current_component_calibration':a.current_component,'relay_carrier':a.relay_carrier,'front_glue_reserve':a.front_glue_reserve,'words':words,'permanent_masses':mass,'explicit_mass_changes':changes,'required_carriers':a.carry,'empty_cases':empty,
       'source_obligations':['G0 source must drive own1/2/3 with correct off; T0 first3 requires separately phase-checked power (shared wmmmw RB withdrawn)','Late4 and sticky fire4 require the explicit pulse/relay construction; carrier choices alone do not establish power','rear RB drives rear2/3','other baseline sources retained but contact/source geometry unproved'],
       'regression':'Failed G0 wmmmw ->T0 late4 direct moving contact3 is excluded by existing static hazard rule.',
       'input_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.base/'problem.flyer',a.base/'failure_audit_0_0_7.json',ROLE]}}
    report['explicit_action_changes']=action_changes
    if action_changes:report['source_obligations'].append('Changed action kinds require new source/switch-off and spatial realization; no baseline hardware acceptance transfers.')
    if status in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
        loads={body:{str(t):mass[body]+sum(solver.Value(v) for v in terms[body,t]) for t,m in enumerate(word) if m} for body,word in mv.items()}
        actions=[]
        for row in records:
            selected=[{'body':b,'touch':bits,'carries_at':active} for b,bits,active,v in row['choices'] if solver.Value(v) and any(bits)]
            actions.append({k:v for k,v in row.items() if k!='choices'}|{'contacts':selected})
        report.update(loads=loads,actions=actions,peak=solver.Value(peak),objective=solver.ObjectiveValue())
    (a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({k:v for k,v in report.items() if k in ['status','seconds','empty_cases','peak','loads']}))


if __name__=='__main__':main()
