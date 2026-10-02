"""Target-driven shared-port bank, including axial drag of competitors.

At each phase-0 pulse, first eligible free normal piston drives the sticky
target. That target carries the other movable pistons at X D0(t), as well as
those on its fixed side port at X D0(t)-1. Their moving flags clear cached
power, so only the winning piston extends. Other phase carriers remain
scheduled as in the contact witness. Payload geometry is still abstract.
"""
import itertools
import json
from pathlib import Path
from observer_contract_snapshot import PORTS, INITIAL


def tick(state,t):
    prepared = []
    powers = []
    actors = []
    for i,(x,s,owner) in enumerate(state):
        power = owner is None and t%3 == 0 and x == (t+1)//3
        powers.append(power)
        if owner is None and s == 0 and power:
            actors.append(('piston',i))
        elif owner is None and s == 1:
            s = 2
        elif owner is None and s == 2 and not power:
            s = 3
        elif owner is None and s == 3:
            actors.append(('piston',i))
        prepared.append([x,s,owner])
    actors += [('start',i) for i,(ph,_) in enumerate(PORTS)
               if ph == t%3 and ph != 0]
    actors += [('finish',i) for i,(ph,_) in enumerate(PORTS) if ph == (t-1)%3]
    following = {}
    for order in itertools.permutations(actors):
        out = [list(q) for q in prepared]
        fired = []
        for kind,i in order:
            if kind == 'piston':
                q = out[i]
                if q[2] is not None:
                    continue
                if q[1] == 3:
                    q[1] = 0
                elif q[1] == 0 and powers[i] and q[0] == state[i][0]:
                    q[1] = 1
                    fired.append(i)
                    # Port1's phase0 carrier is the sticky target.
                    target_x = (t+2)//3
                    for j,other in enumerate(out):
                        if j != i and other[1] == 0 and other[2] is None:
                            if other[0] in (target_x-1,target_x):
                                other[0] += 1
                                other[2] = 1
            elif kind == 'start':
                ph,off = PORTS[i]
                source = off+(t+2-ph)//3
                for q in out:
                    if q[1] == 0 and q[2] is None and q[0] == source:
                        q[0] += 1
                        q[2] = i
            else:
                for q in out:
                    if q[2] == i:
                        q[2] = None
        result = tuple(tuple(q) for q in out)
        following.setdefault(result,{'order':order,'fired':fired})
        if t%3 == 0 and len(fired) != 1:
            return following,{'reason':'target is not moved exactly once',
                              'tick':t,'state':state,'order':order,
                              'fired':fired,'result':result}
    return following,None


def run(ticks=120, initial=INITIAL):
    states = {tuple(initial): []}
    levels = []
    seen = {}
    for t in range(ticks):
        following = {}
        for state,trace in states.items():
            results,failure = tick(state,t)
            if failure:
                return {'valid':False,**failure,'trace':trace,'levels':levels}
            for result,way in results.items():
                following.setdefault(result,trace+[way])
        states = following
        levels.append({'tick':t,'states':len(states)})
        # Every body/carrier displacement increases by1 each3ticks.
        normalized = frozenset(tuple((x-(t+2)//3,s,owner)
                                     for x,s,owner in state) for state in states)
        signature = (t%3,normalized)
        if signature in seen:
            return {'valid':True,'ticks':t+1,'repeat_from_tick':seen[signature],
                    'finite_state_recurrence':True,'levels':levels,
                    'terminal_states':list(states)}
        seen[signature] = t
    return {'valid':True,'ticks':ticks,'finite_state_recurrence':False,
            'levels':levels}


if __name__ == '__main__':
    report = run()
    Path(__file__).with_name('competition.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
