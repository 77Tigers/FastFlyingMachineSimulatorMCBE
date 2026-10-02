"""Conservative abstract order check for fixed side pickup ports.

Carriers perform +X steps at t == phase (mod 3), finishing next tick.
Each port is one isolated transverse neighbor lane; its x coordinate is
offset + floor((t + 2 - phase)/3) before the carrier stage of tick t.
No carrier driving/power mechanism or non-port body geometry is modeled.
Each port belongs to a distinct carrier, even when phases coincide.
All permutations of passenger piston update and individual carrier starts
and finishes are checked, including impossible permutations:
this over-approximation is suitable for proving contact safety only.
"""
import itertools
import json
from pathlib import Path


def step(state, t, period, ports, observer=False):
    x, ps, owner = state
    initial_moving = owner is not None
    powered = (not initial_moving and x == (t+1)//3 and t % 3 == 0
               if observer else t % period == 0 and not initial_moving)
    out = {}
    actors = ['piston']
    actors += [('start', i) for i, (ph, _) in enumerate(ports) if ph == t % 3]
    actors += [('finish', i) for i, (ph, _) in enumerate(ports)
               if ph == (t-1) % 3]
    for order in itertools.permutations(actors):
        q, s, moving_owner = x, ps, owner
        events = []
        fired = False
        for event in order:
            if event == 'piston':
                if moving_owner is not None:
                    continue
                if s == 0 and powered:
                    # Power calculated at tick start is cleared on transport.
                    if initial_moving or q != x:
                        continue
                    s = 1
                    fired = True
                    events.append('extend')
                elif s == 1:
                    s = 2
                    events.append('extension settled')
                elif s == 2 and not (powered and q == x):
                    s = 3
                    events.append('retract')
                elif s == 3:
                    s = 0
                    events.append('retraction settled')
            elif event[0] == 'start':
                i = event[1]
                phase, off = ports[i]
                port_x = off + (t + 2 - phase)//3
                if s == 0 and moving_owner is None and q == port_x:
                    q += 1
                    moving_owner = i
                    events.append(f'pickup port {i}')
            else:
                if moving_owner == event[1]:
                    moving_owner = None
                    events.append('passenger settled')
        result = (q, s, moving_owner)
        out.setdefault(result, []).append({'order': order, 'events': events,
                                          'fired': fired})
    return out


def check(period, ports, cycles=2):
    states = {(0, 0, None): []}
    levels = []
    for t in range(period*cycles):
        following = {}
        for state, trace in states.items():
            for result, ways in step(state, t, period, ports).items():
                for way in ways:
                    if t % period == 0 and not way['fired']:
                        return False, {'failure': 'missed extension', 'tick': t,
                                       'state': state, 'trace': trace + [way]}
                following.setdefault(result, trace + [ways[0]])
        states = following
        levels.append({'tick': t, 'states': sorted(states, key=str)})
        if (t + 1) % period == 0:
            target = ((t + 1)//3, 0, None)
            if set(states) != {target}:
                bad = next(s for s in states if s != target)
                return False, {'failure': 'recurrence mismatch', 'tick': t,
                               'expected': target, 'actual': bad,
                               'trace': states[bad], 'levels': levels}
    return True, {'ports': ports, 'period': period, 'cycles': cycles,
                  'levels': levels, 'terminal_states': list(states)}


if __name__ == '__main__':
    ports = [(1, -1), (0, -1), (2, 0), (1, 0)]
    valid, report = check(12, ports)
    report['valid'] = valid
    output = Path(__file__).with_name('period12.json')
    output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
