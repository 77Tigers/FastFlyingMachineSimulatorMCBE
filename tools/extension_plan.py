"""Cheap phase-contact preflight for periodic extension plans.

Objects are named points, not inferred rigid bodies. This checks only declared
contact obligations at slot boundaries; it does not model power, piston state,
connectivity, intermediate ordering, or routing. Shared points are permitted
unless a contact explicitly constrains them.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PASS_MESSAGE = (
    "CONSISTENT: sparse contact obligations only; power, states, connectivity, "
    "intermediate-order safety and routing unresolved"
)


class PlanError(ValueError):
    """The input is not a valid sparse extension plan."""


def _keys(value: dict[str, Any], required: set[str], allowed: set[str], where: str) -> None:
    missing = required - value.keys()
    unknown = value.keys() - allowed
    if missing:
        raise PlanError(f"{where}: missing field(s): {', '.join(sorted(missing))}")
    if unknown:
        raise PlanError(f"{where}: unknown field(s): {', '.join(sorted(unknown))}")


def _integer(value: Any, where: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise PlanError(f"{where} must be an integer")
    if minimum is not None and value < minimum:
        raise PlanError(f"{where} must be at least {minimum}")
    return value


def _position(value: Any, where: str) -> tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3:
        raise PlanError(f"{where} must be an [x, y, z] integer triple")
    return tuple(_integer(component, f"{where}[{i}]") for i, component in enumerate(value))  # type: ignore[return-value]


def _validate(plan: Any) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise PlanError("plan must be a JSON object")
    root_keys = {"version", "name", "slot_ticks", "period_slots", "advance", "objects", "contacts"}
    _keys(plan, root_keys, root_keys, "plan")
    if _integer(plan["version"], "version") != 1:
        raise PlanError("version must be 1")
    if not isinstance(plan["name"], str) or not plan["name"]:
        raise PlanError("name must be a non-empty string")
    if _integer(plan["slot_ticks"], "slot_ticks", 1) != 2:
        raise PlanError("slot_ticks must be 2")
    period = _integer(plan["period_slots"], "period_slots", 1)
    advance = _integer(plan["advance"], "advance", 0)
    if not isinstance(plan["objects"], list) or not plan["objects"]:
        raise PlanError("objects must be a non-empty array")
    if not isinstance(plan["contacts"], list) or not plan["contacts"]:
        raise PlanError("contacts must be a non-empty array")

    objects: dict[str, dict[str, Any]] = {}
    for index, obj in enumerate(plan["objects"]):
        where = f"objects[{index}]"
        if not isinstance(obj, dict):
            raise PlanError(f"{where} must be an object")
        _keys(obj, {"name", "at", "word"}, {"name", "at", "word"}, where)
        name, word = obj["name"], obj["word"]
        if not isinstance(name, str) or not name:
            raise PlanError(f"{where}.name must be a non-empty string")
        if name in objects:
            raise PlanError(f"duplicate object name: {name}")
        if not isinstance(word, str) or len(word) != period or any(char not in "mw" for char in word):
            raise PlanError(f"{where}.word must contain exactly {period} characters, each 'm' or 'w'")
        if word.count("m") != advance:
            raise PlanError(f"{where}.word must contain exactly {advance} 'm' characters")
        objects[name] = {"at": _position(obj["at"], f"{where}.at"), "word": word}

    contacts: list[dict[str, Any]] = []
    contact_names: set[str] = set()
    for index, contact in enumerate(plan["contacts"]):
        where = f"contacts[{index}]"
        if not isinstance(contact, dict):
            raise PlanError(f"{where} must be an object")
        required = {"name", "a", "b", "slots", "relation"}
        allowed = required | {"offset", "required"}
        _keys(contact, required, allowed, where)
        name = contact["name"]
        if not isinstance(name, str) or not name:
            raise PlanError(f"{where}.name must be a non-empty string")
        if name in contact_names:
            raise PlanError(f"duplicate contact name: {name}")
        contact_names.add(name)
        a, b = contact["a"], contact["b"]
        if not isinstance(a, str) or not isinstance(b, str) or a not in objects or b not in objects:
            raise PlanError(f"{where}.a and .b must name declared objects")
        relation = contact["relation"]
        if not isinstance(relation, str) or relation not in {"adjacent", "same", "offset"}:
            raise PlanError(f"{where}.relation must be 'adjacent', 'same', or 'offset'")
        if relation == "offset":
            if "offset" not in contact:
                raise PlanError(f"{where}.offset is required for relation 'offset'")
            offset = _position(contact["offset"], f"{where}.offset")
        else:
            if "offset" in contact:
                raise PlanError(f"{where}.offset is only valid for relation 'offset'")
            offset = None
        slots = contact["slots"]
        if not isinstance(slots, list) or not slots:
            raise PlanError(f"{where}.slots must be a non-empty array")
        parsed_slots = [_integer(slot, f"{where}.slots[{i}]", 0) for i, slot in enumerate(slots)]
        if any(slot >= period for slot in parsed_slots):
            raise PlanError(f"{where}.slots values must be in 0..{period - 1}")
        if len(set(parsed_slots)) != len(parsed_slots):
            raise PlanError(f"{where}.slots must not contain duplicates")
        required_contact = contact.get("required", True)
        if not isinstance(required_contact, bool):
            raise PlanError(f"{where}.required must be a boolean")
        contacts.append({
            "name": name,
            "a": a,
            "b": b,
            "slots": parsed_slots,
            "relation": relation,
            "offset": offset,
            "required": required_contact,
        })

    return {"name": plan["name"], "period_slots": period, "advance": advance,
            "objects": objects, "contacts": contacts}


def _world_position(obj: dict[str, Any], slot: int, advance: int, cycle: int = 0) -> tuple[int, int, int]:
    x, y, z = obj["at"]
    moves = obj["word"].count("m", 0, slot) + cycle * advance
    return (x + moves, y, z)


def check_plan(plan: Any) -> dict[str, Any]:
    """Return a machine-readable ``consistent`` or ``contradicted`` verdict."""
    checked = _validate(plan)
    objects = checked["objects"]
    for contact in checked["contacts"]:
        for slot in contact["slots"]:
            pos_a = _world_position(objects[contact["a"]], slot, checked["advance"])
            pos_b = _world_position(objects[contact["b"]], slot, checked["advance"])
            vector = tuple(pos_b[i] - pos_a[i] for i in range(3))
            relation = contact["relation"]
            if relation == "same":
                holds = vector == (0, 0, 0)
            elif relation == "adjacent":
                holds = sum(abs(component) for component in vector) == 1
            else:
                holds = vector == contact["offset"]
            if holds != contact["required"]:
                want = "must" if contact["required"] else "must not"
                offset_text = f" with offset {contact['offset']}" if relation == "offset" else ""
                message = (
                    f"CONTRADICTED: contact {contact['name']} at slot {slot} "
                    f"(tick {slot * 2}); {contact['a']} at {pos_a}, {contact['b']} at {pos_b}; "
                    f"actual b-a vector {vector}; {contact['a']} {want} be {relation} "
                    f"{contact['b']}{offset_text}"
                )
                return {
                    "verdict": "contradicted",
                    "name": checked["name"],
                    "message": message,
                    "mismatch": {
                        "contact": contact["name"],
                        "slot": slot,
                        "tick": slot * 2,
                        "obligation": {"relation": relation, "required": contact["required"], "offset": contact["offset"]},
                        "world_positions": {contact["a"]: list(pos_a), contact["b"]: list(pos_b)},
                        "actual_vector_b_minus_a": list(vector),
                    },
                }
    return {"verdict": "consistent", "name": checked["name"], "message": PASS_MESSAGE}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check sparse phase-contact obligations in an extension plan")
    parser.add_argument("plan", type=Path, help="JSON extension plan")
    parser.add_argument("--out", type=Path, help="write the machine-readable verdict as JSON")
    args = parser.parse_args(argv)
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        result = check_plan(plan)
    except (OSError, json.JSONDecodeError, PlanError) as error:
        print(f"invalid plan: {error}", file=sys.stderr)
        return 2
    if args.out:
        try:
            args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        except OSError as error:
            print(f"cannot write verdict: {error}", file=sys.stderr)
            return 2
    print(result["message"])
    return 0 if result["verdict"] == "consistent" else 1


if __name__ == "__main__":
    raise SystemExit(main())
