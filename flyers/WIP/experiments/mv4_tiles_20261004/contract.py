"""Bounded temporal interface census; NOT a simulator or geometry proof.

Run from any directory. Emits one compact JSON summary to stdout, no files.
Coordinates are source locations at the start of the power stage. Movement
starts at t and settles during t+1, so a body is moving at stage start iff
it started at t-1. All words advance four cells per 12 ticks.
"""
import json
import sys
import itertools

PERIOD = 12
H = {4, 6, 8, 10}  # sticky extends 0, pulls 2, resets 3
CORES = {f"mv4_{p}": set(range(p, 12, 3)) for p in range(3)}


def pos(starts, t):
    cycles, rem = divmod(t, PERIOD)
    return 4 * cycles + sum(s < rem for s in starts)


def stationary(starts, t):
    return (t - 1) % PERIOD not in starts


def power_options(helper=H):
    words = dict(CORES)
    for word in ("mmwmmw", "mmmmww"):
        for shift in range(12):
            starts = {(shift + 2*i) % 12 for i, c in enumerate(word) if c == "m"}
            words[f"{word}_{shift}"] = starts
    candidates = []
    # A transverse direct source powers when relative X equals its tick-0
    # value. A non-front axial source likewise has one required X offset.
    for name, starts in words.items():
        for kind in ("redstone", "observer"):
            powered = [t for t in range(12)
                       if stationary(helper, t) and stationary(starts, t)
                       and pos(starts, t) - pos(helper, t) == 0
                       and (kind == "redstone" or (t-2) % 12 in starts)]
            # Power at tick 1 is harmless while extending; power at 2
            # prevents the desired pull; later power risks extra extension.
            if 0 in powered and set(powered) <= {0, 1}:
                candidates.append(dict(source=name, kind=kind, powered=powered,
                                       starts=sorted(starts)))
    return candidates


def passive_leaf_schedules():
    """All four-advance 12-tick schedules with no overlapping 2-tick moves.

    Leaf has no immovable state. Contact is transverse core-glue-to-leaf;
    unlimited faces allowed here, making this a necessary-condition screen.
    """
    results, tested = [], 0
    for comb in itertools.combinations(range(12),4):
        helper = set(comb)
        if any((t+1) % 12 in helper for t in helper):
            continue
        tested += 1
        covered, contacts = set(), []
        for name, starts in CORES.items():
            for delta in sorted({pos(starts,t)-pos(helper,t) for t in range(12)}):
                hits = {t for t in starts if stationary(helper,t)
                        and pos(starts,t)-pos(helper,t) == delta}
                if hits and hits <= helper:
                    covered |= hits
                    contacts.append(dict(core=name,delta=delta,pickups=sorted(hits)))
        if covered == helper:
            results.append(dict(starts=list(comb),contacts=contacts))
    return dict(tested=tested, viable=results,
                scope='Prescribed rigid mv4 cores; passive leaf; transverse adhesive pickup only; fixed schedule; no obstruction or actuator-driven move.')


def glue_contacts():
    records = []
    for name, starts in CORES.items():
        for delta in sorted({pos(starts, t)-pos(H, t) for t in range(12)}):
            active = [t for t in range(12) if stationary(H,t) and stationary(starts,t)
                      and pos(starts,t)-pos(H,t) == delta]
            good = [t for t in active if t in starts and t in H]
            bad = [t for t in active if (t in starts) != (t in H)]
            records.append(dict(core=name, delta=delta, pickups=good,
                                unwanted_moves=bad, viable=bool(good) and not bad))
    return records


def rider_contacts():
    records = []
    for name, starts in CORES.items():
        for delta in sorted({pos(starts,t)-pos(H,t) for t in range(12)}):
            # Only the core recruits a leaf piston; it does not stick back.
            # At ticks 1/2 the piston is immovable in every update order.
            # At tick 3 it can reset before the core starts: reject that race.
            touches = [t for t in starts if stationary(H,t)
                       and pos(starts,t)-pos(H,t) == delta and t not in (1,2)]
            good = sorted(set(touches) & H)
            bad = sorted(set(touches) - H)
            records.append(dict(core=name, delta=delta, pickups=good,
                                unwanted_moves=bad, viable=bool(good) and not bad))
    return records


def reset_sim():
    """Real simulator isolated reset/pickup race, plus state 0/2 controls.

    Uses temporary inputs/outputs, automatically removed. Not a flyer proof.
    Run cargo build --release --bin fastflyer-sim before this mode.
    """
    import pathlib
    import subprocess
    import tempfile
    from collections import Counter
    root = pathlib.Path(__file__).resolve().parents[4]
    sys.path.insert(0, str(root))
    from fastflyer import Flyer, Block, Kind
    exe = root / 'target/release/fastflyer-sim.exe'
    results = {}
    with tempfile.TemporaryDirectory(prefix='mv4_reset_') as tmp:
        a, b = pathlib.Path(tmp)/'in.flyer', pathlib.Path(tmp)/'out.flyer'
        for state in (0,2,3):
            counts = Counter()
            for seed in (0,1,2,5,42):
                for px in (0,7,8,15):
                    for pz in (0,7,8,15):
                        f = Flyer(rng_state=seed, push_limit=12, phase_x=px, phase_z=pz)
                        f.set((-1,0,0), Block(Kind.REDSTONE_BLOCK))
                        f.set((0,0,0), Block.piston(0))
                        f.set((1,0,0), Block(Kind.SLIME))
                        f.set((1,1,0), Block.piston(1, sticky=True, state=state))
                        if state == 2:
                            f.set((0,1,0), Block(Kind.PISTON_ARM))
                        f.save(a)
                        subprocess.run([str(exe),str(a),str(b),'1'], check=True, capture_output=True)
                        g = Flyer.load(b)
                        base = next(p for p,bl in g.blocks() if bl.kind == Kind.PISTON and not bl.sticky)
                        rider = next(p for p,bl in g.blocks() if bl.kind == Kind.PISTON and bl.sticky)
                        counts['carried' if rider[0]-base[0] == 2 else 'left'] += 1
            results[state] = dict(counts)
    assert results[0] == {'carried':80}, results
    assert results[2] == {'left':80}, results
    assert set(results[3]) == {'carried','left'}, results
    return results


def main():
    contacts = glue_contacts()
    # H_e extends at e, pulls at e+2, rides e+4/6/8/10. Twelve
    # translated copies supply every rear-core move and exactly four rides
    # at every current-core move. This accounts for ALL helper advances.
    ledger = [dict(tick=t, core=t % 3, rear_puller=(t-2) % 12,
                   carried_helpers=[e for e in range(12) if (t-e) % 12 in H])
              for t in range(12)]
    assert all(len(row['carried_helpers']) == 4 for row in ledger)
    assert all(sum(e in row['carried_helpers'] for row in ledger) == 4 for e in range(12))
    early = power_options({3,5,7,10})
    robust = [r for r in power_options() if any((r['source'],r['kind']) == (s['source'],s['kind']) for s in early)]
    print(json.dumps(dict(power_options=power_options(), glue_contacts=contacts,
                         rider_contacts=rider_contacts(),
                         early_branch_power_options=early,
                         both_branch_power_options=robust,
                         passive_leaf_schedules=passive_leaf_schedules(),
                         ledger=ledger, limits=[
        'Timing necessary conditions only: no geometry, source adhesion, arm sweep or update-order proof.',
        'Glue contact test assumes stationary rigid glue bodies, transverse adjacency, same material; excludes obstruction and rider interfaces.',
        'Any viable isolated contact still needs simultaneous routing and power isolation.',
        'Twelve-helper architecture budget is core size + four transported helper sizes plus other recruited cells.']), indent=2))


if __name__ == '__main__':
    if '--sim-reset' in sys.argv:
        print(json.dumps(reset_sim(), indent=2))
    else:
        main()
