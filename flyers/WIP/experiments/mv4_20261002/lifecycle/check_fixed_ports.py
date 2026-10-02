"""Bounded lifecycle check; no geometry/simulator modifications.

One normal piston acts at t=0, resets by end t=3, and must travel k
blocks in period 3k. Fixed side pickup ports stay on +X-only bodies
with the three prescribed movement phases. Any same-tick settlement
or reset before an unintended pickup counts as an ordering hazard.
"""
from itertools import combinations


def body_x(t, phase):
    return (t + 2 - phase) // 3


def check(starts, period):
    ports = {(t % 3, sum(s < t for s in starts) - body_x(t, t % 3))
             for t in starts}
    hazards = []
    for t in range(period):
        if t in starts:
            continue
        # State 1/2 cannot become movable; state3 reset at t3 can.
        if t < 3:
            continue
        relative = sum(s < t for s in starts) - body_x(t, t % 3)
        if (t % 3, relative) in ports:
            hazards.append(t)
    return hazards


def main():
    simple = (4, 6, 8, 10)
    print('12-tick state-only witness:', simple,
          'fixed-port unintended pickup ticks:', check(simple, 12))
    for k in range(2, 9):
        period = 3 * k
        tested = 0
        witnesses = []
        for starts in combinations(range(4, period - 1), k):
            if any(b - a < 2 for a, b in zip(starts, starts[1:])):
                continue
            tested += 1
            if not check(starts, period):
                witnesses.append(starts)
        print(f'period={period}: {tested} lifecycle itineraries; '
              f'{len(witnesses)} order-robust fixed side-port witnesses')
        if witnesses:
            print('first:', witnesses[0])


if __name__ == '__main__':
    main()
