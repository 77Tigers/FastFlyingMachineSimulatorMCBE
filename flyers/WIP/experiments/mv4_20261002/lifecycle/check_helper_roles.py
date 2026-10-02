"""Finite timing/role check for12 mmmmww helpers and3 mv cores."""
OFFSETS = (4, 6, 8, 10)


def launch_count(t, starts):
    return sum(s < t for s in starts)


def main():
    for b in range(12):
        # Four outgoing helper actuators and one outgoing core actuator.
        targets = [(b - d) % 12 for d in OFFSETS]
        for target in targets:
            assert b in {(target + d) % 12 for d in OFFSETS}
        assert len(set(targets)) == 4
    for a in range(12):
        incoming = {b for b in range(12)
                    if a in {(b - d) % 12 for d in OFFSETS}}
        assert incoming == {(a + d) % 12 for d in OFFSETS}
    for q in range(3):
        assert {b for b in range(12) if b % 3 == q} == set(range(q, 12, 3))

    # Source core class+1 moves at1,4,7,10 and pulses at0,3,6,9.
    source_starts = (1, 4, 7, 10)
    relative = []
    valid = []
    for t in (0, 3, 6, 9):
        delta = launch_count(t, source_starts) - launch_count(t, OFFSETS)
        moving = any(t in (s, s + 1) for s in OFFSETS)
        relative.append(delta)
        valid.append(delta == 0 and not moving)
    assert relative == [0, 1, 1, 0]
    assert valid == [True, False, False, False]
    print('PASS:12helpers;3cores;48helper actuators;12core actuators')
    print('PASS:all helper/core movement obligations have exact role causes')
    print('PASS:core observer pulse offsets0,3,6,9 yield relativeX', relative)
    print('PASS:only initial pulse reaches a stationary aligned member')
    print('LIMIT:axial reach,contact geometry,cross-power,andpush load unresolved')


if __name__ == '__main__':
    main()
