"""Exhaustive slot-level check of 'rigid-heavy' N6 schedules (victim V's frame, one pusher column model).

V-local slots 0..7: V rests 0,1; W (next) rests 2,3; O rests 4,5; U (previous) rests 6,7.
Each of V's six moves (slots 2..7) is done either by one of V's hopping pushers ('H') or by a rigid piston
on a resting body:
  W2  W pusher pushes at 2 (W rests 2,3; V rested at 1)            race-free
  W3  W sticky pulls at 3 (extends 2)    after-pull race at 4 (V and W both move, V block at sticky face)
  O5  O sticky pulls at 5 (extends 4)    after-pull race at 6
  U7  U sticky pulls at 7 (extends 6)    race-free (V rests at 0)
  O4/U6 rigid pushes: pusher sat touching co-moving V glue in the slot before -> fatal (pushes V with O/U)
Hopper power sources (lateral to the hopper column at V-frame x = rel_Y(s) + c, start of slot s):
  RB on body Y (always on) or observer on body Y (on in the slot after Y moved), Y in V,W,O,U.
Drag rule: V's plate glue sits at x=1 in the hopper column (the hopper's push target), so a foreign
source at x=1 (strict: also x=2) at the start of a slot in which V moves and Y rests is dragged by V
(fatal); if both move it is a +1-rider race.
Hoppers powered by the same kind of source race (any powered ready hopper may fire), so every firing
order is explored.  A hopper is ready (pos 0, riding V) from slot 2 until it fires, at -1 the slot after,
at -2 while W carries it, and back to 0 after W's moves at 0,1 (fired at 7: -1, -1).
usage: python rigid_schedules.py [strict]
"""
import sys, itertools

STRICT = 'strict' in sys.argv[1:]
MOVES = {'V': {2, 3, 4, 5, 6, 7}, 'W': {4, 5, 6, 7, 0, 1}, 'O': {6, 7, 0, 1, 2, 3}, 'U': {0, 1, 2, 3, 4, 5}}
RIGID = {2: 'W2', 3: 'W3', 5: 'O5', 7: 'U7'}
RACE_AFTER = {'W3': 4, 'O5': 6}


def rel(Y, s):
    """Y minus V displacement at the start of V-local slot s (counted from slot 0)."""
    return sum((t in MOVES[Y]) - (t in MOVES['V']) for t in range(s))


def hopper_pos(k):
    """V-frame x of a hopper that fires at slot k, at the start of slots 0..7, plus its state at start."""
    pos, st = {}, {}
    for s in range(8):
        if 2 <= s <= k: pos[s], st[s] = 0, 0
        elif s == k + 1: pos[s], st[s] = -1, 2                       # extended, must retract now
        elif s > k + 1: pos[s], st[s] = -2, 0
    if k == 7: pos[0], st[0], pos[1], st[1] = -1, 2, -1, 0
    else: pos[0], st[0], pos[1], st[1] = -2, 0, -1, 0
    return pos, st


def src_x(src, s):
    Y, kind, c = src
    return rel(Y, s) + c


def src_on(src, s):
    Y, kind, c = src
    return kind == 'RB' or ((s - 1) % 8) in MOVES[Y]


def drag(src):
    """None if fatal drag, else number of +1 race slots."""
    Y, kind, c = src
    if Y == 'V': return 0
    races = 0
    bad = {1, 2} if STRICT else {1}
    for s in range(8):
        if src_x(src, s) in bad:
            vm, ym = s in MOVES['V'], s in MOVES[Y]
            if vm and not ym: return None
            if vm and ym: races += 1
    return races


def powered(src, k, s):
    pos, _ = hopper_pos(k)
    return src_on(src, s) and src_x(src, s) == pos[s]


SOURCES = [(Y, kind, c) for Y in 'VWOU' for kind in ('RB', 'OBS') for c in range(-3, 4)]
SOURCES = [s for s in SOURCES if not (s[0] == 'V' and s[2] != 0)]
SOURCES = [s for s in SOURCES if any(src_x(s, t) == 0 for t in range(2, 8))]


def check(rigid, srcs):
    """explore all firing orders; return (ok, worst extra riders) for hopper sources srcs."""
    hslots = [s for s in range(2, 8) if s not in rigid]
    if len(srcs) != len(hslots): return False, 'count'
    worst = [0]

    def rec(s, fired):
        if s == 8:
            # every hopper fired once; check misfires/stuck for all slots given fire slots
            for i, k in fired.items():
                pos, st = hopper_pos(k)
                for t in range(8):
                    p = powered(srcs[i], k, t)
                    if 2 <= t <= k: continue   # ready: handled by the race recursion
                    if p: return f'hopper{i}({srcs[i]}) fired@{k} powered at {t} (pos {pos[t]} state {st[t]})'
            return None
        ready = [i for i in range(len(srcs)) if i not in fired]
        live = [i for i in ready if src_on(srcs[i], s) and src_x(srcs[i], s) == 0]
        if s in rigid:
            if live: return f'slot {s} rigid {rigid[s]} but hoppers {live} powered'
            return rec(s + 1, fired)
        if not live: return f'slot {s}: no powered ready hopper'
        for i in live:
            r = rec(s + 1, {**fired, i: s})
            if r: return r
        return None
    r = rec(2, {})
    return (r is None), r


def main():
    ok_src = [s for s in SOURCES if drag(s) is not None]
    print(f'{len(SOURCES)} hopper sources reach the ready cell; {len(ok_src)} survive the drag rule (strict={STRICT}):')
    for s in ok_src:
        fires = [k for k in range(2, 8) if powered(s, k, k)]
        print('  ', s, 'races', drag(s), 'on@ready', [t for t in range(2, 8) if src_on(s, t) and src_x(s, t) == 0])
    print()
    for r in range(0, 5):
        for combo in itertools.combinations(sorted(RIGID), r):
            rigid = {k: RIGID[k] for k in combo}
            n = 6 - len(rigid)
            found = []
            for ms in itertools.combinations_with_replacement(range(len(ok_src)), n):
                srcs = [ok_src[i] for i in ms]
                good, why = check(rigid, srcs)
                if good: found.append(srcs)
            extra = sum(1 for k in rigid.values() if k in RACE_AFTER)
            tag = ', '.join(rigid.values()) or 'none (pure race design)'
            if found:
                kinds = sorted({tuple(sorted(set(f))) for f in found}, key=len)
                print(f'rigid {{{tag}}}: {len(found)} feasible source multisets; after-pull race riders +{extra}; e.g.')
                for f in found[:4]: print('     ', f)
            else:
                print(f'rigid {{{tag}}}: INFEASIBLE')


if __name__ == '__main__':
    main()
