"""Lift the existing five-phase carrier plan onto a closed 20-module ring.

This checks the role-model equations, not spatial contacts or physical power.
No MILP or layout search is run. Geometry, column races and source placement
remain explicit obligations; fourfold geometry is not implied by phase closure.
"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "pl11_3bps_20261013/model/stacked_plan.json"
MODEL = HERE.parent / "tm_smol_rebalance_20261001/j2_front_smol/layered.py"


def main():
    spec = importlib.util.spec_from_file_location("carrier_role_model", MODEL)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    template = {ast.literal_eval(k): v for k, v in json.loads(OLD.read_text(encoding="utf-8")).items()}
    count = 20
    shifts = {"X": 0, "T": 3, "G": 6, "H": 9}
    # Includes glue and non-piston hardware; glued sticky pistons are riders.
    # H6 must reserve RB + observer, leaving at most four glue cells.
    mass = {"X": 8, "T": 7, "G": 8, "H": 6}
    words = {}
    for i in range(count):
        for role, shift in shifts.items():
            phase = (-2 * i + shift) % 5
            words[f"{role}{i}"] = [int((t - phase) % 5 < 3) for t in range(5)]
    loads = {(name, t): mass[name[0]] for name, word in words.items() for t in range(5) if word[t]}
    actions = []
    for name, vm in words.items():
        i = int(name[1:])
        for slot in range(5):
            if not vm[slot]:
                continue
            matches = [(key, carriers) for key, carriers in template.items()
                       if key[0] == f"{name[0]}{i % 5}" and key[1] == slot]
            assert len(matches) == 1
            (_, _, kind), carriers = matches[0]
            firing, frozen, pm, rel = model.trajectory(vm, kind, slot)
            lifted = []
            for source, bits in carriers:
                delta = (int(source[1:]) - i % 5 + 2) % 5 - 2
                carrier = f"{source[0]}{(i + delta) % count}"
                flags = tuple(map(int, bits))
                assert flags in model.options(vm, words[carrier], carrier == name,
                                               kind, firing, frozen, pm, rel)
                for t in range(5):
                    if pm[t] and words[carrier][t] and flags[t]:
                        loads[carrier, t] += 1
                lifted.append({"body": carrier, "touch": bits})
            for t in range(5):
                assert not pm[t] or any(words[c["body"]][t] and int(c["touch"][t]) for c in lifted)
            role = name[0]
            power_body = name if kind == "push" else {"X": f"G{i}", "T": f"H{i}", "G": f"H{i}"}[role]
            power_kind = "observer" if kind == "pull" and role == "G" else "redstone_block"
            if power_kind == "observer":
                assert words[power_body][(firing - 1) % 5] and not words[power_body][firing]
            actions.append({"target": name, "slot": slot, "kind": kind,
                            "firing_slot": firing, "piston_moves": pm,
                            "carriers": lifted,
                            "power_obligation": {"source_body": power_body, "kind": power_kind,
                                                 "on": firing, "off_by": (firing + 1) % 5,
                                                 "spatial_and_order_verified": False}})
    assert len(actions) == 240
    assert all(words[f"{r}{i}"] == words[f"{r}{(i + 5) % count}"]
               for r in shifts for i in range(count))
    peak = max(loads.values())
    result = {
        "scope": "closed20-module role-model lift; no geometry, physical power or flyer verification",
        "rear_segments": count, "total_glue_bodies": len(words),
        "phase_closes_after": 5, "quarter_turn_maps_module": "+5 modulo20",
        "quarter_turn_geometry_verified": False,
        "material_assignment_verified": False,
        "optimistic_permanent_mass": mass,
        "helper_mass_caveat": "H6 reserves RB+observer and therefore <=4 glue; shape not constructed",
        "maximum_role_load": peak,
        "fits_requested_PL12_role_budget": peak <= 12,
        "rear_maximum_role_load": max(v for (n, _), v in loads.items() if n.startswith("X")),
        "words": {k: "".join("m" if b else "w" for b in v) for k, v in words.items()},
        "loads": {f"{n}:{t}": v for (n, t), v in loads.items()},
        "actions": actions,
        "unresolved": ["closed fourfold geometry and collision clearance",
                       "glue material compatibility and required contact distances",
                       "source placement and switch-off including normal-column identity races",
                       "all sticky power and recovery in actual natural simulation",
                       "complete independent80 and80x10000 verification"],
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (OLD, MODEL, Path(__file__))},
    }
    out = HERE / "results/quarter_ring20_role_plan.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("scope", "rear_segments", "total_glue_bodies", "maximum_role_load", "rear_maximum_role_load")}))


if __name__ == "__main__":
    main()
