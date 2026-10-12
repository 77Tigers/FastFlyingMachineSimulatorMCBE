#!/usr/bin/env python3
"""Explain a tagged-port movement miss from the simulator's real trace.

This is a diagnostic view, not a repair tool or a second full simulator.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DIRECTIONS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
SLIME, HONEY, SMOOTH, GLAZED, REDSTONE, OBSERVER, ROD, PISTON, ARM = 1, 2, 3, 5, 6, 7, 8, 9, 10
SOLID = {SLIME, HONEY, SMOOTH, GLAZED}


def _pos(row: list[Any] | tuple[int, int, int]) -> tuple[int, int, int]:
    return (int(row[0]), int(row[1]), int(row[2]))


def _initial(trace: dict[str, Any]) -> dict[tuple[int, int, int], int]:
    return {_pos(row): int(row[3]) for row in trace["initial"]}


def _move_map(movement: Any) -> dict[tuple[int, int, int], tuple[int, int, int]]:
    if not isinstance(movement, dict):
        return {}
    sources, destinations = movement.get("sources"), movement.get("destinations")
    if not isinstance(sources, list) or not isinstance(destinations, list):
        return {}
    return {_pos(src): _pos(dst) for src, dst in zip(sources, destinations)}


def _apply_changes(cells: dict[tuple[int, int, int], int], changes: list[Any]) -> None:
    for row in changes:
        pos = _pos(row)
        if row[3] is None:
            cells.pop(pos, None)
        else:
            cells[pos] = int(row[3])


def _offset(pos: tuple[int, int, int], direction: int) -> tuple[int, int, int]:
    delta = DIRECTIONS[direction]
    return tuple(pos[i] + delta[i] for i in range(3))  # type: ignore[return-value]


def _kind(cell: int) -> int:
    return cell & 15


def _moving(cell: int) -> bool:
    return bool(cell & 16)


def _direction(cell: int) -> int:
    return (cell >> 5) & 7


def _state(cell: int) -> int:
    return (cell >> 10) & 3


def _hard_powered(cells: dict[tuple[int, int, int], int]) -> set[tuple[int, int, int]]:
    result: set[tuple[int, int, int]] = set()
    for pos, cell in cells.items():
        kind = _kind(cell)
        if _moving(cell) or not (kind == ROD or (kind == OBSERVER and cell & 0x100)):
            continue
        target = _offset(pos, _direction(cell))
        if (target in cells and not _moving(cells[target])
                and _kind(cells[target]) in SOLID):
            result.add(target)
    return result


def _power_facts(pos: tuple[int, int, int], cell: int,
                 cells: dict[tuple[int, int, int], int], hard: set[tuple[int, int, int]]) -> dict[str, Any]:
    facing = _direction(cell)
    front = _offset(pos, facing)
    adjacent = []
    soft = []
    hard_neighbors = []
    for delta in DIRECTIONS:
        neighbor = tuple(pos[i] + delta[i] for i in range(3))
        source = cells.get(neighbor)
        if neighbor == front:
            if source is not None and _kind(source) in (REDSTONE, ROD, OBSERVER):
                adjacent.append({"at": list(neighbor), "kind": _kind(source),
                                 "moving": _moving(source), "ignored_front": True})
            continue
        if neighbor in hard:
            hard_neighbors.append(list(neighbor))
        if source is None or _moving(source):
            continue
        kind = _kind(source)
        eligible = kind in (REDSTONE, ROD) or (
            kind == OBSERVER and bool(source & 0x100)
            and _offset(neighbor, _direction(source)) == pos
        )
        if kind in (REDSTONE, ROD, OBSERVER):
            adjacent.append({"at": list(neighbor), "kind": kind, "moving": False,
                             "observer_powered": bool(source & 0x100) if kind == OBSERVER else None,
                             "observer_faces_piston": (_offset(neighbor, _direction(source)) == pos)
                                 if kind == OBSERVER else None,
                             "eligible_soft": eligible, "ignored_front": False})
        if eligible:
            soft.append(list(neighbor))
    power_eligible = not _moving(cell)
    return {"piston_moving": _moving(cell), "power_eligible": power_eligible,
            "powered_at_pre_power": power_eligible and bool(soft or hard_neighbors),
            "soft_sources": soft, "hard_powered_neighbors": hard_neighbors,
            "adjacent_power_sources": adjacent}


def _immovable(cell: int, owner: tuple[int, int, int]) -> bool:
    kind = _kind(cell)
    return _moving(cell) or kind == ARM or (kind == PISTON and _state(cell) != 0)


def _sticks(left: int, right: int) -> bool:
    a, b = _kind(left), _kind(right)
    if b == GLAZED:
        return False
    return not ((a == SLIME and b == HONEY) or (a == HONEY and b == SLIME))


def _geometric_reach(owner: tuple[int, int, int], cell: int,
                     target: tuple[int, int, int],
                     cells: dict[tuple[int, int, int], int]) -> dict[str, Any] | None:
    """Approximate an extension's forward/adhesion closure; does not prove legality."""
    direction = _direction(cell)
    queue = [_offset(owner, direction)]
    selected: set[tuple[int, int, int]] = set()
    blocked = False
    while queue:
        pos = queue.pop()
        if pos in selected:
            continue
        block = cells.get(pos)
        if block is None:
            continue
        selected.add(pos)
        if pos == owner or _immovable(block, owner):
            blocked = True
            continue
        destination = _offset(pos, direction)
        if destination in cells and destination not in selected:
            queue.append(destination)
        if _kind(block) in (SLIME, HONEY):
            for delta in DIRECTIONS:
                neighbor = tuple(pos[i] + delta[i] for i in range(3))
                other = cells.get(neighbor)
                if other is not None and neighbor != owner and not _immovable(other, owner) \
                        and _sticks(block, other):
                    queue.append(neighbor)
    if target not in selected:
        return None
    return {"visited_closure_blocks": len(selected), "blocked_neighbor_seen": blocked,
            "legal_extension_proof": False,
            "limits": ["push limit, destination conflicts, and complete simulator legality are not proved"]}


def _source_tracks(cells: dict[tuple[int, int, int], int]) -> list[dict[str, Any]]:
    tracks = []
    for pos, cell in sorted(cells.items()):
        if _kind(cell) in (REDSTONE, ROD, OBSERVER):
            tracks.append({"origin": pos, "at": pos, "moves": []})
    return tracks


def _source_at(tracks: list[dict[str, Any]], pos: tuple[int, int, int]) -> dict[str, Any] | None:
    for track in tracks:
        if track["at"] == pos:
            return track
    return None


def analyze(rows: list[dict[str, Any]], port_at: tuple[int, int, int], tick: int,
            *, port_name: str = "input", word: str | None = None,
            period_ticks: int | None = None) -> dict[str, Any]:
    if tick < 0 or tick >= len(rows):
        raise ValueError("trace does not include requested tick")
    cells = _initial(rows[0])
    if port_at not in cells or _kind(cells[port_at]) == ARM:
        raise ValueError(f"no tagged permanent block at port coordinate {port_at}")
    tagged = {"origin": port_at, "at": port_at, "moves": []}
    tracks = _source_tracks(cells)
    target_snapshot = None
    target_port_pos = None
    target_source_tracks = None
    target_hard_power = None
    target_power_by_pos = {}
    target_candidates = []
    actual_actions = []
    observed_move = None

    for current_tick, trace in enumerate(rows[:tick + 1]):
        incoming = _initial(trace)
        if incoming != cells:
            raise ValueError(f"trace tick {current_tick} snapshot does not match prior tick result")
        if current_tick == tick:
            target_snapshot = dict(cells)
            target_port_pos = tagged["at"]
            target_source_tracks = [{"origin": track["origin"], "at": track["at"],
                                     "moves": list(track["moves"])} for track in tracks]
            target_hard_power = _hard_powered(cells)
            target = tagged["at"]
            for pos, cell in sorted(cells.items()):
                if _kind(cell) != PISTON:
                    continue
                power = _power_facts(pos, cell, cells, target_hard_power)
                target_power_by_pos[pos] = power
                if _moving(cell):
                    continue
                reach = _geometric_reach(pos, cell, target, cells)
                if reach is None:
                    continue
                target_candidates.append({"at": list(pos), "facing": _direction(cell),
                    "state": _state(cell), "sticky": bool(cell & 0x100), "angry": bool(cell & 0x200),
                    "geometric_candidate": True, "state_zero_ready": _state(cell) == 0,
                    **power, "reach": reach})
        for step in trace.get("steps", []):
            actor = step.get("active_piston")
            action = step.get("action")
            movement = step.get("movement")
            mapping = _move_map(movement)
            if current_tick == tick and actor is not None:
                actor_pos = _pos(actor)
                actor_cell = cells.get(actor_pos)
                tag_source = tagged["at"] in mapping
                if sum(abs(actor_pos[i] - tagged["at"][i]) for i in range(3)) <= 4 or tag_source:
                    actual_actions.append({"at": list(actor_pos), "action": action,
                        "state_at_action": _state(actor_cell) if actor_cell is not None and _kind(actor_cell) == PISTON else None,
                        "facing_at_action": _direction(actor_cell) if actor_cell is not None and _kind(actor_cell) == PISTON else None,
                        "powered_at_pre_power": target_power_by_pos.get(actor_pos, {}).get("powered_at_pre_power"),
                        "failure": (movement or {}).get("failure") if isinstance(movement, dict) else None,
                        "moved_tagged_port": tag_source})
            if tagged["at"] in mapping:
                old, new = tagged["at"], mapping[tagged["at"]]
                tagged["moves"].append({"tick": current_tick, "from": list(old), "to": list(new),
                                        "actor": actor, "action": action})
                tagged["at"] = new
                if current_tick == tick:
                    observed_move = {"from": list(old), "to": list(new), "actor": actor, "action": action}
            for track in tracks:
                old = track["at"]
                if old in mapping:
                    new = mapping[old]
                    track["moves"].append({"tick": current_tick, "from": list(old), "to": list(new),
                                           "actor": actor, "action": action})
                    track["at"] = new
            _apply_changes(cells, step.get("changes", []))

    assert target_snapshot is not None and target_port_pos is not None and target_source_tracks is not None and target_hard_power is not None
    expected = None
    if word is not None and period_ticks:
        slot = (tick % period_ticks) // 2
        if tick % 2 == 0 and slot < len(word):
            expected = "move +X" if word[slot] == "m" else "wait"
        elif tick % 2:
            expected = "wait"
    sources = []
    relevant_positions = set()
    anchors = [tuple(candidate["at"]) for candidate in target_candidates] or [target_port_pos]
    for candidate in target_candidates:
        relevant_positions.update(tuple(p) for p in candidate["soft_sources"])
        relevant_positions.update(tuple(p) for p in candidate["hard_powered_neighbors"])
        for source in candidate["adjacent_power_sources"]:
            relevant_positions.add(tuple(source["at"]))
    for pos, cell in target_snapshot.items():
        if _kind(cell) in (REDSTONE, ROD, OBSERVER) and min(
                sum(abs(pos[i] - anchor[i]) for i in range(3)) for anchor in anchors) <= 2:
            relevant_positions.add(pos)
    for pos in sorted(relevant_positions):
        cell = target_snapshot.get(pos)
        if cell is None:
            continue
        track = _source_at(target_source_tracks, pos)
        sources.append({"at": list(pos), "kind": _kind(cell), "moving": _moving(cell),
                        "powered_observer": bool(cell & 0x100) if _kind(cell) == OBSERVER else None,
                        "origin": list(track["origin"]) if track else None,
                        "moves": track["moves"][-6:] if track else []})
    return {"version": 1, "tick": tick,
            "port": {"name": port_name, "origin": list(tagged["origin"]),
                     "at_tick_start": list(target_port_pos),
                     "expected": expected,
                     "observed": "moved" if observed_move else "did not move",
                     "movement": observed_move, "history": tagged["moves"]},
            "candidate_pushers": target_candidates,
            "candidate_scope": "extension front, forward obstructions, and adhesion only; sticky pull reach is not enumerated",
            "actual_piston_actions_near_port": actual_actions,
            "relevant_power_sources": sources,
            "mechanics_note": "Powered status is computed from the pre-power snapshot using SIMULATION.md rules. Candidate pushers are approximate geometric reach, not proof of a legal extension or a complete actuator inventory."}


def _trace_executable() -> Path:
    names = ("extension-trace.exe", "extension-trace")
    for directory in (ROOT / "target" / "release", ROOT / "target" / "debug"):
        for name in names:
            path = directory / name
            if path.is_file():
                return path
    raise FileNotFoundError("extension-trace binary not found under target/release or target/debug")


def _load_port(args: argparse.Namespace) -> tuple[tuple[int, int, int], str, str | None, int | None]:
    if args.contract:
        from extension_contract import load_contract
        contract = load_contract(args.contract)
        ports = contract.ports
        port = next((p for p in ports if p.name == args.port_name), None) if args.port_name else \
            next((p for p in ports if p.role == "input"), ports[0] if ports else None)
        if port is None:
            raise ValueError("contract has no matching port")
        if args.port is not None and tuple(args.port) != port.at:
            raise ValueError("--port conflicts with selected contract port")
        return port.at, port.name, port.word, contract.period_ticks
    if args.port is None:
        raise ValueError("provide --contract or --port X Y Z")
    return tuple(args.port), args.port_name or "input", None, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("flyer", type=Path, help=".flyer file to trace")
    parser.add_argument("--contract", type=Path, help="contract JSON; first input port is used by default")
    parser.add_argument("--port-name", help="select a named contract port")
    parser.add_argument("--port", nargs=3, type=int, metavar=("X", "Y", "Z"),
                        help="explicit tagged-port coordinate")
    parser.add_argument("--tick", type=int, required=True, help="zero-based failed tick")
    parser.add_argument("--rng", type=int, help="optional extension-trace RNG override")
    parser.add_argument("--phase-x", type=int, help="optional world phase X override")
    parser.add_argument("--phase-z", type=int, help="optional world phase Z override")
    args = parser.parse_args(argv)
    try:
        if args.tick < 0:
            raise ValueError("tick must be nonnegative")
        if args.contract is not None and not args.contract.is_absolute():
            args.contract = Path.cwd() / args.contract
        port_at, name, word, period = _load_port(args)
        overrides = (args.rng, args.phase_x, args.phase_z)
        if any(value is not None for value in overrides):
            if any(value is None for value in overrides):
                raise ValueError("--rng, --phase-x, and --phase-z must be supplied together")
            if not 0 <= args.phase_x <= 15 or not 0 <= args.phase_z <= 15:
                raise ValueError("phase overrides must be between 0 and 15")
        command = [str(_trace_executable()), str(args.flyer), str(args.tick + 1)]
        if args.rng is not None:
            command.extend(str(value) for value in overrides)
        output = subprocess.check_output(command, text=True, encoding="utf-8")
        rows = [json.loads(line) for line in output.splitlines() if line.strip()]
        report = analyze(rows, port_at, args.tick, port_name=name, word=word, period_ticks=period)
        print(json.dumps(report, separators=(",", ":"), sort_keys=True))
        return 0
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as exc:
        print(f"extension-explain: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
