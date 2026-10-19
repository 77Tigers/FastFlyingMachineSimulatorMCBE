"""Attribute a natural trace's action loads to glue bodies and hardware kinds.

Diagnostic only: consumes extension-trace JSONL and its normalized natural
contract; does not select candidates or certify a design.
The stroke_budgets table groups all actions by body and slot, retaining peak
kind counts and an identity-attributed example even below the global peak.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path


def audit(contract, trace):
    if not trace:
        raise ValueError("empty trace")
    ports = contract["ports"]
    initial = trace[0]["initial"]
    cells = {tuple(row[:3]): row[3] for row in initial}
    origins = {p: p for p, cell in cells.items() if cell & 15 != 10}
    kinds = {p: cell & 15 for p, cell in cells.items() if cell & 15 != 10}
    body_of = {}
    for port in ports:
        start = tuple(port["at"])
        if start in body_of:
            continue
        material = cells[start] & 15
        if material not in (1, 2):
            raise ValueError(f"non-glue port: {port['name']}")
        pending = [start]
        body_of[start] = port["name"]
        while pending:
            p = pending.pop()
            for axis in range(3):
                for delta in (-1, 1):
                    q = list(p)
                    q[axis] += delta
                    q = tuple(q)
                    if q not in body_of and cells.get(q, 0) & 15 == material:
                        body_of[q] = port["name"]
                        pending.append(q)
    actions = []
    failures = []
    for tick in trace:
        permanent = {tuple(r[:3]) for r in tick["initial"] if r[3] & 15 != 10}
        if permanent != set(origins):
            raise ValueError("trace identity map differs at tick boundary")
        for step in tick["steps"]:
            movement = step.get("movement")
            if not movement:
                continue
            if movement["failure"]:
                partial = [origins[tuple(p)] for p in movement["sources"] if tuple(p) in origins]
                failures.append({
                    "tick": step["tick"], "failure": movement["failure"],
                    "actor": step.get("active_piston"), "partial_discovery_only": True,
                    "partial_source_count": len(movement["sources"]),
                    "partial_kind_counts": dict(sorted(Counter(kinds[p] for p in partial).items())),
                    "partial_body_counts": dict(sorted(Counter(body_of[p] for p in partial if p in body_of).items())),
                    "hardware_origins": [list(p) for p in partial if p not in body_of],
                })
                continue
            sources = [tuple(p) for p in movement["sources"]]
            destinations = [tuple(p) for p in movement["destinations"]]
            if len(sources) != len(destinations) or len(set(destinations)) != len(destinations):
                raise ValueError("invalid movement mapping")
            if not sources:
                continue
            moved = [origins[p] for p in sources]
            bodies = sorted({body_of[p] for p in moved if p in body_of})
            actor_at = tuple(step["active_piston"]) if step.get("active_piston") is not None else None
            actor_origin = origins.get(actor_at)
            actions.append({
                "tick": step["tick"], "slot": step["tick"] % contract["period_ticks"] // 2,
                "action": step["action"], "actor": step["active_piston"],
                "bodies": bodies, "load": len(sources),
                "kinds": dict(sorted(Counter(kinds[p] for p in moved).items())),
                "hardware_origins": [list(p) for p in moved if p not in body_of],
                "actor_origin": list(actor_origin) if actor_origin is not None else None,
            })
            for p in sources:
                del origins[p]
            origins.update(zip(destinations, moved))
    grouped = defaultdict(list)
    for action in actions:
        grouped["+".join(action["bodies"])].append(action)
    maximum = max((a["load"] for a in actions), default=0)
    actuator_roles = {}
    for action in actions:
        origin = action["actor_origin"]
        if origin is None:
            continue
        key = ",".join(map(str, origin))
        entry = actuator_roles.setdefault(key, {
            "origin": origin, "initial_cell": cells[tuple(origin)], "actions": 0,
            "targets": [],
        })
        entry["actions"] += 1
        target = {"slot": action["slot"], "action": action["action"], "bodies": action["bodies"]}
        if target not in entry["targets"]:
            entry["targets"].append(target)
    # Retain whole-stroke accounting even when a rear body is below the
    # flyer's global maximum. Kind counts include every passenger, not only
    # the glue component named by the port.
    stroke_budgets = {}
    for body, rows in sorted(grouped.items()):
        slots = {}
        for slot in sorted({a["slot"] for a in rows}):
            strokes = [a for a in rows if a["slot"] == slot]
            peak = max(a["load"] for a in strokes)
            examples = [a for a in strokes if a["load"] == peak]
            slots[str(slot)] = {
                "actions": len(strokes),
                "min_load": min(a["load"] for a in strokes),
                "max_load": peak,
                "peak_kind_counts": [dict(items) for items in sorted({
                    tuple(a["kinds"].items()) for a in examples
                })],
                "example_at_maximum": examples[0],
            }
        stroke_budgets[body] = slots
    return {
        "diagnostic_only": True, "ticks": len(trace), "permanent_blocks": len(origins),
        "failures": failures, "max_load": maximum,
        "load_histogram": dict(sorted(Counter(a["load"] for a in actions).items())),
        "bodies": {body: {
            "actions": len(rows), "min_load": min(a["load"] for a in rows),
            "max_load": max(a["load"] for a in rows),
            "at_maximum": sum(a["load"] == maximum for a in rows),
        } for body, rows in sorted(grouped.items())},
        "peak_actions": [a for a in actions if a["load"] == maximum],
        "stroke_budgets": stroke_budgets,
        "actuator_roles": actuator_roles,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("trace", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8-sig"))
    trace = [json.loads(line) for line in args.trace.read_text(encoding="utf-8-sig").splitlines()]
    result = audit(contract, trace)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("ticks", "permanent_blocks", "max_load", "load_histogram", "bodies", "failures")}))
