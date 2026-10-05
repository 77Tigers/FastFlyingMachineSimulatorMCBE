"""Finite 12-rt timing screen for one front-mounted backward sticky.

This is deliberately kinematic. It does not claim an adhesive contact layout,
an order-robust piston schedule, or a completed flyer.
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORDS = {"mmwmmw": "mmwmmw", "mmmmww": "mmmmww"}


def moves(word, shift):
    return sorted((shift + 2 * i) % 12 for i, letter in enumerate(word) if letter == "m")


def core_displacement(phase, tick):
    # Each phase moves at t == phase (mod 3), with the phase-2 core at x=0 at t=0.
    return (tick + 2 - phase) // 3


records = []
for name, word in WORDS.items():
    for shift in range(0, 12, 2):
        starts = moves(word, shift)
        busy = {(t + dt) % 12 for t in starts for dt in (0, 1)}
        waits = [t for t in range(12) if all((t + dt) % 12 not in busy for dt in range(4))]
        # A standard sticky needs four stationary ticks: extend, finish,
        # retract/pull, reset. Restrict pull to the phase-2 peak core.
        for wait in waits:
            pull = (wait + 2) % 12
            if pull % 3 != 2:
                continue
            for initial_axial_offset in range(-2, 5):
                helper_before = initial_axial_offset + sum(t < pull for t in starts)
                core_before = core_displacement(2, pull)
                if helper_before - core_before != 2:
                    continue
                records.append({
                    "word": name,
                    "shift_rt": shift,
                    "move_starts": starts,
                    "wait_start": wait,
                    "pull_tick": pull,
                    "initial_helper_base_minus_phase2_core": initial_axial_offset,
                    "helper_carriers": [
                        {"tick": t, "phase": t % 3,
                         "base_minus_carrier_core_before": initial_axial_offset
                         + sum(s < t for s in starts) - core_displacement(t % 3, t)}
                        for t in starts
                    ],
                })

# Align the pull to the observed first peak at tick 122 == 2 (mod 12).
selected = next(r for r in records if r["word"] == "mmmmww" and r["pull_tick"] == 2)
starts = set(selected["move_starts"])
rows = []
for tick in range(12):
    if tick == 0:
        sticky = "observer pulse powers sticky; extend into empty front"
    elif tick == 1:
        sticky = "power off; finish extension"
    elif tick == 2:
        sticky = "power off; retract and pull phase-2 rear core"
    elif tick == 3:
        sticky = "finish reset"
    elif tick in (6, 8, 10):
        sticky = "unwanted own-observer pulse at ride start; gating unresolved"
    elif tick == 11:
        sticky = "helper observer finishes moving; queues tick-0 pulse"
    else:
        sticky = "idle"
    rows.append({
        "tick": tick,
        "rear_core_phase": tick % 3,
        "rear_core_initiator": "front helper sticky pull" if tick == 2 else "rear core actuator",
        "helper": "carried by rear core phase " + str(tick % 3) if tick in starts
                  else "settles prior ride" if (tick - 1) % 12 in starts else "stationary",
        "sticky_and_power": sticky,
    })

result = {
    "screen": "six even rotations per word; axial offsets -2..4; four stationary ticks required",
    "candidates": records,
    "selected": selected,
    "table": rows,
    "limits": [
        "An observer fixed beside the sticky also powers it at ticks 6,8,10 before intended transport; the proposed own-observer power connection is not order-robust. A selective power interface is required.",
        "Carriage contacts, glue material, source location, and update-order closure are unproved.",
        "Carrying the helper at four rear-core moves can increase those loads; no PL reduction is claimed.",
        "The phase-2 rear core still has three native actuator moves and one assisted pull per 12rt.",
    ],
}
(HERE / "helper_contract.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"counts_by_word": {word: sum(r["word"] == word for r in records) for word in WORDS},
                  "selected": selected}, indent=2))
