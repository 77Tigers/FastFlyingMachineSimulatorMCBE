"""Full sampled-block ledger for the proposed G0 third-stroke retiming.

Replay baseline ownership from the verified143-cell audit, then reassign
every affected piston. A budget check, not timing/contact/power acceptance.
"""
import argparse,hashlib,json
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    audit=a.base/'failure_audit_0_0_7.json';data=json.loads(audit.read_text(encoding='utf-8'))
    words={p['name']:p['word'] for p in json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))['ports']}
    permanent={};pistons={};baseline={}
    for action in data['actions']:
        if action['tick']>=10:continue
        assert len(action['moved_ports'])==1
        body=action['moved_ports'][0];slot=action['tick']//2
        fixed={tuple(i[4]) for i in action['identities'] if i[3]&15!=9}
        if body in permanent:assert permanent[body]==fixed
        else:permanent[body]=fixed
        baseline[body,slot]=action['successful_load']
        for i in action['identities']:
            if i[3]&15==9:
                origin=tuple(i[4]);assert slot not in pistons.setdefault(origin,{})
                pistons[origin][slot]=body
    # Nominal piston identities can exchange: some move2/4 times in a sampled
    # period. Preserve those actual untouched assignments, not a guessed3.
    for (body,slot),load in baseline.items():
        assert load==len(permanent[body])+sum(carriers.get(slot)==body for carriers in pistons.values())
    changes={
        (17,0,14):{0:'T0',2:'G0',4:'G0'}, # first G0 actor fires1
        (21,1,13):{2:'G0',3:'X1',4:'H0'}, # first spent H0 actor
        (21,3,13):{0:'H0',3:'T0',4:'H0'}, # second spent H0 actor
        (20,2,14):{1:'G0',2:'G0',3:'T0'}, # H0 late actor fires4
        (19,2,13):{1:'G0',2:'G0',3:'T0'}, # sticky fires4/pulls0
        (15,2,11):{1:'G0',2:'G0',3:'T0'}, # T0 late actor fires4
    }
    new_words={**words,'G0':'wmmwm'};new_pistons={**pistons,**changes}
    mass={b:len(cells) for b,cells in permanent.items()}
    mass['T0']+=1 # -RB +observer +non-adhesive hard-power relay
    loads={(body,s):mass[body] for body,word in new_words.items() for s,ch in enumerate(word) if ch=='m'}
    for origin,carriers in new_pistons.items():
        for slot,body in carriers.items():
            assert new_words[body][slot]=='m',(origin,slot,body)
            loads[body,slot]+=1
    report={'scope':__doc__,'baseline_sha256':hashlib.sha256(audit.read_bytes()).hexdigest(),
            'sample_only':True,'nominal_identity_exchange_allowed':True,
            'words':new_words,'permanent_mass':mass,'changed_pistons':[{'origin':p,'before':pistons[p],'after':v} for p,v in changes.items()],
            'loads':{b:{str(s):v for (body,s),v in loads.items() if body==b} for b in words},
            'overloads':[{'body':b,'slot':s,'load':v,'over':v-12} for (b,s),v in loads.items() if v>12],
            'unbuilt':['G0 first2 and T0 first3 shared RB geometry/off','G0 third4 receives pulse rather than static RB','new recovery contacts including X1 first-H0 pickup3','new observer/relay geometry and all natural moves'],
            'remaining_supplied_rear_pushes':[2,3]}
    (a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'loads':report['loads'],'overloads':report['overloads']}))


if __name__=='__main__':main()
