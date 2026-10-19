"""Independently check exported contact scaffolds using integer coordinates."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rot(p, q):
    x, y, z = p
    for _ in range(q % 4): y, z = -z, y
    return x, y, z


def shift(p, s): return p[0]+s, p[1], p[2]
def pref(word, t): return sum(c == 'm' for c in word[:t])
def distance(a, b): return sum(abs(x-y) for x,y in zip(a,b))


def check(result):
    plan = json.loads((HERE/'results/quarter_ring20_role_plan.json').read_text(encoding='utf-8'))
    glue = {}
    power = {}
    for name, cells in result['glue'].items():
        assert cells and len(cells) <= {'X':7,'T':6}[name[0]]
        i=int(name[1:]); radius=result['radius']; step=i*2*radius//5
        y,z=(step,-radius) if step<=radius else (radius,step-2*radius)
        if name[0]=='X':
            assert tuple(cells[0][1:])==(y,z)
            assert all(-2<=p[0]<=2 and abs(p[1]-y)<=2 and abs(p[2]-z)<=2 for p in cells)
        else:
            assert all(1<=p[0]<=7 and abs(p[1]-y)<=3 and abs(p[2]-z)<=3 for p in cells)
        pts = set(map(tuple,cells))
        assert len(pts) == len(cells)
        seen = {next(iter(pts))}
        while True:
            expanded = seen | {p for p in pts if any(distance(p,q)==1 for q in seen)}
            if expanded == seen: break
            seen = expanded
        assert seen == pts, f'disconnected {name}'
        for q in range(1 if result.get('local_modules') else 4):
            glue[f'{name[0]}{int(name[1:])+5*q}'] = [rot(p,q) for p in cells]
    for name,p in result.get('redstone_sources',{}).items():
        i=int(name[1:]); radius=result['radius']; step=i*2*radius//5
        y,z=(step,-radius) if step<=radius else (radius,step-2*radius)
        assert -3<=p[0]<=8 and abs(p[1]-y)<=4 and abs(p[2]-z)<=4
        assert any(distance(p,g)==1 for g in glue[name]), 'source not carried by glue'
        for q in range(1 if result.get('local_modules') else 4):
            power[f'{name[0]}{i+5*q}']=rot(p,q)
    if result.get('reserved_redstone_sources'): assert set(power)==set(glue)
    count = 0
    for actor in result['actors']:
        a = next(a for a in plan['actions'] if (a['target'],a['slot']) == (actor['target'],actor['slot']))
        p = tuple(actor['at'])
        i=int(a['target'][1:]); step=i*2*result['radius']//5; radius=result['radius']
        y,z=(step,-radius) if step<=radius else (radius,step-2*radius)
        assert -5<=p[0]<=10 and abs(p[1]-y)<=4 and abs(p[2]-z)<=4
        assert actor['moves'] == a['piston_moves'] and actor['kind'] == a['kind']
        if result.get('reserved_redstone_sources') and a['kind']=='push':
            for tick,on in ((a['firing_slot'],True),((a['firing_slot']+1)%5,False)):
                rb=shift(power[a['target']],pref(plan['words'][a['target']],tick))
                piston=shift(p,sum(a['piston_moves'][:tick]))
                delta=tuple(x-y for x,y in zip(rb,piston))
                powered=delta in ((-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
                assert powered==on, f'normal on/off source mismatch {a["target"]}:{tick}'
        t = a['slot']
        target = shift(p, sum(a['piston_moves'][:t])+(1 if a['kind']=='push' else -2))
        assert target in [shift(g,pref(plan['words'][a['target']],t)) for g in glue[a['target']]]
        for c in a['carriers']:
            if result.get('local_modules') and c['body'] not in result['active_body_names']: continue
            if result['open_quadrant_seams'] and int(c['body'][1:])//5 != int(a['target'][1:])//5: continue
            for t, bit in enumerate(c['touch']):
                if bit == '1':
                    now = shift(p,sum(a['piston_moves'][:t]))
                    assert any(distance(now, shift(g,pref(plan['words'][c['body']],t)))==1 for g in glue[c['body']])
                    count += 1
    extra_contacts = []
    for t in range(5):
        occupied = []
        for name, cells in glue.items():
            occupied += [shift(g,pref(plan['words'][name],t)) for g in cells]
            if name in power: occupied.append(shift(power[name],pref(plan['words'][name],t)))
        for actor in result['actors']:
            a = next(a for a in plan['actions'] if (a['target'],a['slot']) == (actor['target'],actor['slot']))
            for q in range(1 if result.get('local_modules') else 4):
                p = rot(shift(actor['at'],sum(actor['moves'][:t])),q)
                occupied.append(p)
                if t == (a['firing_slot']+1)%5: occupied.append(shift(p,1 if a['kind']=='push' else -1))
                if actor['moves'][t]:
                    expected = {f"{c['body'][0]}{(int(c['body'][1:])+5*q)%20}"
                                for c in a['carriers'] if c['touch'][t]=='1'}
                    for name, cells in glue.items():
                        if plan['words'][name][t]=='m' and name not in expected and any(
                            distance(p,shift(g,pref(plan['words'][name],t)))==1 for g in cells):
                            extra_contacts.append({'body':name,'slot':t,
                                                   'actor_target':f"{a['target'][0]}{int(a['target'][1:])+5*q}",
                                                   'actor_slot':a['slot']})
        assert len(set(occupied)) == len(occupied), f'collision at {t}'
    assert count == result['recorded_contacts']
    if result.get('forbid_extra_moving_carriers'): assert not extra_contacts, 'extra rider contact'
    if result.get('conservative_compatibility'):
        materials=result['materials']
        assert set(materials)==set(glue) and all(v in (0,1) for v in materials.values())
        for t in range(5):
            positions={n:[shift(p,pref(plan['words'][n],t)) for p in cells] for n,cells in glue.items()}
            for n,cells in positions.items():
                for other,points in positions.items():
                    if n>=other or materials[n]!=materials[other]: continue
                    if plan['words'][n][t]=='m' or plan['words'][other][t]=='m':
                        assert not any(distance(p,q)==1 for p in cells for q in points), 'same-material body contact'
            for owner,rp in power.items():
                for other,points in positions.items():
                    if owner!=other and plan['words'][other][t]=='m':
                        assert not any(distance(shift(rp,pref(plan['words'][owner],t)),q)==1 for q in points), 'foreign RB pickup'
        for actor in result['actors']:
            a=next(a for a in plan['actions'] if (a['target'],a['slot'])==(actor['target'],actor['slot']))
            t=(a['firing_slot']+1)%5
            for q in range(1 if result.get('local_modules') else 4):
                p=rot(shift(actor['at'],sum(actor['moves'][:t])),q)
                front=shift(p,1 if actor['kind']=='push' else -1)
                assert not any(distance(p,shift(rp,pref(plan['words'][owner],t)))==1 and
                               shift(rp,pref(plan['words'][owner],t))!=front for owner,rp in power.items()), 'stray retraction power'
    return {'passed':True,'contact_obligations_checked':count,'body_count':len(glue),
            'normal_on_off_sources_checked':bool(power),
            'conservative_compatibility_checked':bool(result.get('conservative_compatibility')),
            'unplanned_moving_carrier_contacts':extra_contacts,
            'scope':'integer geometry and optional normal on/off sources; sticky/stray power, materials, action order and natural verification remain open'}


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('result',type=Path)
    args=ap.parse_args(); result=json.loads(args.result.read_text(encoding='utf-8'))
    assert result['status'] in ('OPTIMAL','FEASIBLE'), 'no feasible scaffold to check'
    checked=check(result)
    args.result.with_suffix('.checked.json').write_text(json.dumps(checked,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(checked))
