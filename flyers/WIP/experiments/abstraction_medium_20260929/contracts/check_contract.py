"""Small arithmetic check of the frozen stages 1–4 handoff.

This checks transport arithmetic and word representation only. It does not
simulate piston mechanics, test geometry, or establish arbitrary order freedom.
Run from the repository root with:
    python flyers/WIP/experiments/abstraction_medium_20260929/contracts/check_contract.py
"""

from dataclasses import dataclass


SLOT_TICKS = 2
HARDWARE_TICKS = 8
initial = {"A": 0, "B": 2, "A0": 2, "A1": 2, "B0": 4, "B1": 3,
           "O_A": 2, "O_B": 4}
# At an even tick the named body moves +1 X, carrying exactly these named
# hardware passengers. Puller and concurrent resetter do not ride that move.
slots = [
    (0, "A", ("A1", "B1", "O_A"), "A0", "B0", 0, 1),
    (2, "B", ("A0", "B1", "O_B"), "B0", "A1", 2, 3),
    (4, "A", ("A0", "B0", "O_A"), "A1", "B1", 1, 2),
    (6, "B", ("A1", "B0", "O_B"), "B1", "A0", 3, 4),
]
expected_before = [
    {"A": 0, "B": 2, "A0": 2, "A1": 2, "B0": 4, "B1": 3, "O_A": 2, "O_B": 4},
    {"A": 1, "B": 2, "A0": 2, "A1": 3, "B0": 4, "B1": 4, "O_A": 3, "O_B": 4},
    {"A": 1, "B": 3, "A0": 3, "A1": 3, "B0": 4, "B1": 5, "O_A": 3, "O_B": 5},
    {"A": 2, "B": 3, "A0": 4, "A1": 3, "B0": 5, "B1": 5, "O_A": 4, "O_B": 5},
]
expected_reset_arm = {"B0": 3, "A1": 2, "B1": 4, "A0": 3}

positions = initial.copy()
for index, (tick, body, passengers, puller, resetter, source, destination) in enumerate(slots):
    assert tick == index * SLOT_TICKS
    assert positions == expected_before[index], (tick, positions, expected_before[index])
    assert positions[body] == source, (tick, body, "source")
    assert positions[puller] - 2 == source, (tick, puller, "-X pull reach")
    assert positions[puller] - 1 == destination, (tick, puller, "destination")
    assert positions[resetter] - 1 == expected_reset_arm[resetter], (tick, resetter, "reset arm")
    assert puller not in passengers and resetter not in passengers
    print(f"tick {tick}: {body} {source}->{destination}; {puller} base {positions[puller]}; "
          f"{resetter} empty arm {positions[resetter]-1}; passengers {','.join(passengers)}")
    positions[body] += 1
    for passenger in passengers:
        positions[passenger] += 1

assert positions == {name: x + 2 for name, x in initial.items()}, positions
print("tick 8 boundary: all two bodies and six hardware elements translated +2 X")


@dataclass(frozen=True)
class MotionWord:
    word: str
    slot_ticks: int
    hardware_ticks: int

    def __post_init__(self):
        assert self.word and set(self.word) <= {"m", "w"}
        assert self.hardware_ticks == len(self.word) * self.slot_ticks

    def phased(self, slot_shift: int) -> str:
        n = len(self.word)
        return "".join(self.word[(i - slot_shift) % n] for i in range(n))

    def starts(self, slot_shift: int = 0) -> list[int]:
        return [i * self.slot_ticks for i, c in enumerate(self.phased(slot_shift)) if c == "m"]

    def shortest_period_slots(self) -> int:
        return next(p for p in range(1, len(self.word) + 1)
                    if len(self.word) % p == 0 and self.word == self.word[:p] * (len(self.word) // p))

    @property
    def displacement(self) -> int:
        return self.word.count("m")


for word, hardware, shift, expected_starts, expected_phased, displacement, shortest in [
    ("mwmw", 8, 1, [2, 6], "wmwm", 2, 2),
    ("mmwmmw", 12, 1, [2, 4, 8, 10], "wmmwmm", 4, 3),
]:
    contract = MotionWord(word, SLOT_TICKS, hardware)
    assert contract.starts() == ([0, 4] if word == "mwmw" else [0, 2, 6, 8])
    assert contract.phased(shift) == expected_phased
    assert contract.starts(shift) == expected_starts
    assert contract.displacement == displacement
    assert contract.shortest_period_slots() == shortest
    assert contract.hardware_ticks > shortest * SLOT_TICKS
    print(f"{word}: slot={SLOT_TICKS} ticks, shifted={expected_phased}, "
          f"shifted starts={expected_starts}, displacement=+{displacement}, "
          f"shortest word period={shortest*SLOT_TICKS} ticks, hardware cycle={hardware} ticks")
