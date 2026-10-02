"""Extend the contact automaton with actual phase-1 observer pulses.

Pulse at t==0 (mod3), observer at D_1(t)=(t+1)//3. Distinct lane
passengers have distinct carriers and therefore independent ordering choices.
Start four members in one chosen nominal period12 itinerary phase each.
The allowed initial states are taken from the contact witness at time0.
"""
import itertools
import json
from pathlib import Path
from check import step

PORTS = [(1,-1),(0,-1),(2,0),(1,0)]
# Shifted nominal 0,3,6,9 firing phases at global time0; all contacts have
# identical x offsets, placed in distinct transverse lanes.
INITIAL = [(0,0,None),(0,0,2),(-1,0,None),(-1,3,None)]


def run(ticks=120):
    states = [{initial} for initial in INITIAL]
    snapshots = []
    for t in range(ticks):
        following = []
        per_member_fire = []
        for member, options in enumerate(states):
            results = set()
            flags = set()
            for state in options:
                for result, ways in step(state,t,12,PORTS,observer=True).items():
                    results.add(result)
                    for way in ways:
                        flags.add(way['fired'])
                        if way['fired'] and (t%3 != 0 or state[0] != (t+2)//3):
                            return {'valid':False,'reason':'extension misses target',
                                    'tick':t,'member':member,'state':state,'way':way}
            following.append(results)
            per_member_fire.append(sorted(flags))
        if t%3 == 0 and not any(flags == [True] for flags in per_member_fire):
            return {'valid':False,'reason':'all members can miss same pulse',
                    'tick':t,'states':[sorted(ss,key=str) for ss in states],
                    'per_member_fire':per_member_fire,'snapshots':snapshots}
        states = following
        snapshots.append({'tick':t,'states':[sorted(ss,key=str) for ss in states],
                          'per_member_fire':per_member_fire})
    return {'valid':True,'ticks':ticks,'snapshots':snapshots}


if __name__ == '__main__':
    report = run()
    Path(__file__).with_name('observer.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='snapshots'},indent=2))
