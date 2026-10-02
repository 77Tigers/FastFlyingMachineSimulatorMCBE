"""Observer-power bank with four ports shared across four transverse lanes.

Each carrier transports every passenger whose lane-specific port aligns.
Thus start/finish events are shared while passenger reset events may reorder.
"""
import itertools
import json
from pathlib import Path
from observer import PORTS, INITIAL


def tick(state, t):
    prepared = []
    fired = []
    actors = []
    for i,(x,s,owner) in enumerate(state):
        power = owner is None and t%3 == 0 and x == (t+1)//3
        fires = owner is None and s == 0 and power
        fired.append(fires)
        if fires:
            s = 1
        elif owner is None and s == 1:
            s = 2
        elif owner is None and s == 2 and not power:
            s = 3
        elif owner is None and s == 3:
            actors.append(('reset',i))
        prepared.append([x,s,owner])
    actors += [('start',i) for i,(ph,_) in enumerate(PORTS) if ph == t%3]
    actors += [('finish',i) for i,(ph,_) in enumerate(PORTS) if ph == (t-1)%3]
    following = set()
    for order in itertools.permutations(actors):
        out = [list(q) for q in prepared]
        for kind,i in order:
            if kind == 'reset':
                out[i][1] = 0
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
        following.add(tuple(tuple(q) for q in out))
    return following,fired


def run(ticks=60):
    states = {tuple(INITIAL)}
    levels = []
    for t in range(ticks):
        following = set()
        for state in states:
            results,fires = tick(state,t)
            if t%3 == 0 and not any(fires):
                return {'valid':False,'reason':'whole bank misses pulse',
                        'tick':t,'state':state,'levels':levels}
            following.update(results)
        states = following
        levels.append({'tick':t,'states':len(states)})
    return {'valid':True,'ticks':ticks,'levels':levels}


if __name__ == '__main__':
    report = run()
    Path(__file__).with_name('shared.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
