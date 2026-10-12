#!/usr/bin/env python3
"""Validate a self-running FastFlyer extension against a JSON contract.

The trace driver emits one JSON record per zero-based tick. Tick numbers are
carried by the trace's steps. Contracts describe one movement opportunity every
two ticks: the even tick starts a move and the following odd tick settles it.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
ARMS_KIND = 10
SAMPLES = [(rng, px, pz) for rng in (0, 1, 2, 5, 42)
           for px in (0, 7, 8, 15) for pz in (0, 7, 8, 15)]


class ContractError(ValueError):
    pass


def _keys(obj: dict[str, Any], required: set[str], optional: set[str], where: str) -> None:
    missing = required - obj.keys()
    unknown = obj.keys() - required - optional
    if missing:
        raise ContractError(f"{where}: missing field(s): {', '.join(sorted(missing))}")
    if unknown:
        raise ContractError(f"{where}: unknown field(s): {', '.join(sorted(unknown))}")


def _int(value: Any, where: str, *, minimum: int | None = None) -> int:
    if type(value) is not int or (minimum is not None and value < minimum):
        suffix = f" (minimum {minimum})" if minimum is not None else ""
        raise ContractError(f"{where}: expected integer{suffix}")
    return value


def _coord(value: Any, where: str) -> tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3:
        raise ContractError(f"{where}: expected [x, y, z]")
    return tuple(_int(v, where) for v in value)  # type: ignore[return-value]


@dataclass(frozen=True)
class Port:
    name: str
    role: str
    at: tuple[int, int, int]
    word: str
    baseline: tuple[int | None, ...] | None
    spare: tuple[int | None, ...] | None


@dataclass(frozen=True)
class DriveEvent:
    tick: int
    target: tuple[int, int, int]
    limit: int

    @property
    def piston(self) -> tuple[int, int, int]:
        return (self.target[0] - 1, self.target[1], self.target[2])

    @property
    def redstone(self) -> tuple[int, int, int]:
        return (self.target[0] - 2, self.target[1], self.target[2])

    @property
    def arm(self) -> tuple[int, int, int]:
        return self.target


@dataclass(frozen=True)
class PrescribedEvent:
    tick: int
    input: tuple[int, int, int]
    limit: int


@dataclass(frozen=True)
class Contract:
    name: str
    flyer: Path
    period_ticks: int
    advance: int
    cycles: int
    ports: tuple[Port, ...]
    recurrence: str = "exact"
    boundary_envelope: tuple[tuple[int, int, int], tuple[int, int, int]] | None = None
    drive_script: Path | None = None
    drives: tuple[DriveEvent, ...] = ()
    prescribed_script: Path | None = None
    prescribed_order: str | None = None
    prescribed: tuple[PrescribedEvent, ...] = ()


def _read_drive_script(path: Path, period_ticks: int, total_ticks: int) -> tuple[DriveEvent, ...]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ContractError(f"cannot read drive_script {path}: {exc}") from exc
    events = []
    seen = set()
    for line_number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue
        fields = stripped.split()
        where = f"drive_script:{line_number}"
        if len(fields) != 5 or any(re.fullmatch(r"-?[0-9]+", part) is None for part in fields):
            raise ContractError(f"{where}: expected five integer columns: tick x y z limit")
        tick, x, y, z, limit = (int(part, 10) for part in fields)
        _int(tick, f"{where}.tick", minimum=0)
        _int(limit, f"{where}.limit", minimum=1)
        if tick % 2:
            raise ContractError(f"{where}.tick: drive ticks must be even")
        if tick + 3 >= total_ticks:
            raise ContractError(f"{where}.tick: piston cleanup tick must be before totalTicks")
        if tick % period_ticks + 4 > period_ticks:
            raise ContractError(f"{where}.tick: drive fixture lifecycle crosses a period boundary")
        event = DriveEvent(tick, (x, y, z), limit)
        key = (event.tick, *event.target)
        if key in seen:
            raise ContractError(f"{where}: duplicate drive event {key}")
        seen.add(key)
        events.append(event)
    if not events:
        raise ContractError(f"drive_script {path}: expected at least one drive row")
    return tuple(events)


def _read_prescribed_script(path: Path, period_ticks: int, total_ticks: int) -> tuple[PrescribedEvent, ...]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ContractError(f"cannot read prescribed_script {path}: {exc}") from exc
    events = []
    seen = set()
    previous_tick = -1
    for line_number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue
        fields = stripped.split()
        where = f"prescribed_script:{line_number}"
        if len(fields) != 5 or any(re.fullmatch(r"-?[0-9]+", part) is None for part in fields):
            raise ContractError(f"{where}: expected five integer columns: tick x y z max_load")
        tick, x, y, z, limit = (int(part, 10) for part in fields)
        _int(tick, f"{where}.tick", minimum=0)
        _int(limit, f"{where}.max_load", minimum=1)
        if tick % 2:
            raise ContractError(f"{where}.tick: prescribed start ticks must be even")
        if tick + 1 >= total_ticks:
            raise ContractError(f"{where}.tick: settlement tick must be before totalTicks")
        if tick % period_ticks + 2 > period_ticks:
            raise ContractError(f"{where}.tick: prescribed lifecycle crosses a period boundary")
        if tick < previous_tick:
            raise ContractError(f"{where}.tick: prescribed rows must be in nondecreasing tick order")
        previous_tick = tick
        key = (tick, (x, y, z))
        if key in seen:
            raise ContractError(f"{where}: duplicate prescribed input {key[1]} at tick {tick}")
        seen.add(key)
        events.append(PrescribedEvent(tick, (x, y, z), limit))
    if not events:
        raise ContractError(f"prescribed_script {path}: expected at least one prescribed row")
    return tuple(events)


def _loads(value: Any, where: str, slots: int) -> tuple[int | None, ...] | None:
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != slots:
        raise ContractError(f"{where}: expected an array of {slots} nonnegative integers or nulls")
    result = []
    for i, item in enumerate(value):
        result.append(None if item is None else _int(item, f"{where}[{i}]", minimum=0))
    return tuple(result)


def _port_position_at(port: Port, tick: int, period_ticks: int) -> tuple[int, int, int]:
    slots = period_ticks // 2
    prefix = sum(char == "m" for char in port.word[:(tick % period_ticks) // 2])
    cycles = tick // period_ticks
    return (port.at[0] + cycles * port.word.count("m") + prefix, port.at[1], port.at[2])


def load_contract(path: Path) -> Contract:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read contract {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ContractError("contract: expected a JSON object")
    _keys(raw, {"version", "name", "flyer", "period_ticks", "advance", "ports"},
          {"cycles", "recurrence", "boundary_envelope", "drive_script",
           "prescribed_script", "prescribed_order"}, "contract")
    if raw["version"] != 1 or type(raw["version"]) is not int:
        raise ContractError("contract.version: expected 1")
    if not isinstance(raw["name"], str) or not raw["name"].strip():
        raise ContractError("contract.name: expected a nonempty string")
    if not isinstance(raw["flyer"], str) or not raw["flyer"]:
        raise ContractError("contract.flyer: expected a relative path")
    flyer_path = Path(raw["flyer"])
    if flyer_path.is_absolute():
        raise ContractError("contract.flyer: path must be relative to the contract")
    period = _int(raw["period_ticks"], "contract.period_ticks", minimum=2)
    if period % 2:
        raise ContractError("contract.period_ticks: must be even")
    advance = _int(raw["advance"], "contract.advance", minimum=1)
    cycles = _int(raw.get("cycles", 3), "contract.cycles", minimum=1)
    if "drive_script" in raw and "prescribed_script" in raw:
        raise ContractError("contract: drive_script and prescribed_script are mutually exclusive")
    drive_script = None
    drives: tuple[DriveEvent, ...] = ()
    if "drive_script" in raw:
        if not isinstance(raw["drive_script"], str) or not raw["drive_script"]:
            raise ContractError("contract.drive_script: expected a relative path")
        drive_relative = Path(raw["drive_script"])
        if drive_relative.is_absolute():
            raise ContractError("contract.drive_script: path must be relative to the contract")
        drive_script = path.parent / drive_relative
        drives = _read_drive_script(drive_script, period, period * cycles)
    prescribed_script = None
    prescribed_order = None
    prescribed: tuple[PrescribedEvent, ...] = ()
    if "prescribed_script" in raw or "prescribed_order" in raw:
        if not isinstance(raw.get("prescribed_script"), str) or not raw["prescribed_script"]:
            raise ContractError("contract.prescribed_script: expected a relative path")
        if raw.get("prescribed_order") not in ("before_natural", "after_natural"):
            raise ContractError("contract.prescribed_order: expected 'before_natural' or 'after_natural'")
        prescribed_relative = Path(raw["prescribed_script"])
        if prescribed_relative.is_absolute():
            raise ContractError("contract.prescribed_script: path must be relative to the contract")
        prescribed_script = path.parent / prescribed_relative
        prescribed_order = raw["prescribed_order"]
        prescribed = _read_prescribed_script(prescribed_script, period, period * cycles)
    recurrence = raw.get("recurrence", "exact")
    if recurrence not in ("exact", "bounded"):
        raise ContractError("contract.recurrence: expected 'exact' or 'bounded'")
    envelope = None
    if recurrence == "bounded":
        value = raw.get("boundary_envelope")
        if not isinstance(value, dict):
            raise ContractError("contract.boundary_envelope: required object for bounded recurrence")
        _keys(value, {"min", "max"}, set(), "contract.boundary_envelope")
        lower = _coord(value["min"], "contract.boundary_envelope.min")
        upper = _coord(value["max"], "contract.boundary_envelope.max")
        if any(lower[i] > upper[i] for i in range(3)):
            raise ContractError("contract.boundary_envelope: min must be <= max on every axis")
        envelope = (lower, upper)
    elif "boundary_envelope" in raw:
        raise ContractError("contract.boundary_envelope: only allowed with recurrence 'bounded'")
    if not isinstance(raw["ports"], list) or not raw["ports"]:
        raise ContractError("contract.ports: expected a nonempty array")
    ports = []
    names: set[str] = set()
    for i, item in enumerate(raw["ports"]):
        where = f"contract.ports[{i}]"
        if not isinstance(item, dict):
            raise ContractError(f"{where}: expected an object")
        _keys(item, {"name", "role", "at", "word"},
              {"spare_load", "baseline_load"}, where)
        if not isinstance(item["name"], str) or not item["name"].strip():
            raise ContractError(f"{where}.name: expected a nonempty string")
        if item["name"] in names:
            raise ContractError(f"{where}.name: duplicate port name {item['name']!r}")
        names.add(item["name"])
        role = item["role"]
        if role not in ("input", "output"):
            raise ContractError(f"{where}.role: expected 'input' or 'output'")
        word = item["word"]
        if not isinstance(word, str) or len(word) != period // 2 or any(c not in "mw" for c in word):
            raise ContractError(f"{where}.word: expected {period // 2} characters from 'm' and 'w'")
        if role != "input" and ("spare_load" in item or "baseline_load" in item):
            raise ContractError(f"{where}: load budgets are allowed on input ports only")
        if any(key in item and item[key] is None for key in ("baseline_load", "spare_load")):
            raise ContractError(f"{where}: load arrays must be omitted or contain per-slot values")
        baseline = _loads(item.get("baseline_load"), f"{where}.baseline_load", period // 2)
        spare = _loads(item.get("spare_load"), f"{where}.spare_load", period // 2)
        ports.append(Port(item["name"], role, _coord(item["at"], f"{where}.at"),
                          word, baseline, spare))
    contract = Contract(raw["name"], path.parent / flyer_path, period, advance, cycles,
                        tuple(ports), recurrence, envelope, drive_script, drives,
                        prescribed_script, prescribed_order, prescribed)
    motion_error = _validate_word_motion(contract)
    if motion_error:
        raise ContractError(motion_error)
    for event in contract.prescribed:
        slot = (event.tick % period) // 2
        matches = [port for port in contract.ports if port.role == "input" and
                   port.word[slot] == "m" and _port_position_at(port, event.tick, period) == event.input]
        if len(matches) != 1:
            raise ContractError(f"prescribed_script tick {event.tick}: target {event.input} does not identify exactly one declared moving INPUT at its expected phase coordinate")
    for port in contract.ports:
        if port.role != "input" or (port.baseline is None and port.spare is None):
            continue
        for slot, char in enumerate(port.word):
            if char == "m" and (port.baseline is None or port.baseline[slot] is None):
                raise ContractError(f"port {port.name}: baseline_load must be nonnull for moving slot {slot}")
            if char == "m" and port.spare is not None and port.spare[slot] is None:
                raise ContractError(f"port {port.name}: spare_load must be nonnull for moving slot {slot}")
    return contract


def _parse_initial(trace: dict[str, Any]) -> tuple[dict[tuple[int, int, int], int], tuple[tuple[tuple[int, int, int], tuple[int, int, int]], ...]]:
    cells: dict[tuple[int, int, int], int] = {}
    for i, row in enumerate(trace.get("initial", [])):
        if not isinstance(row, list) or len(row) != 4 or type(row[3]) is not int:
            raise ContractError(f"trace.initial[{i}]: malformed cell row")
        pos = tuple(row[:3])
        if pos in cells:
            raise ContractError(f"trace.initial: duplicate cell at {pos}")
        cells[pos] = row[3]
    owners = tuple(sorted((_coord(pair[0], "trace.initial_owners.owner"),
                           _coord(pair[1], "trace.initial_owners.member"))
                          for pair in trace.get("initial_owners", [])))
    return cells, owners


def _apply_changes(cells: dict[tuple[int, int, int], int], changes: Any, where: str) -> None:
    if not isinstance(changes, list):
        raise ContractError(f"{where}.changes: expected an array")
    for i, change in enumerate(changes):
        if not isinstance(change, list) or len(change) != 4:
            raise ContractError(f"{where}.changes[{i}]: malformed change")
        pos = tuple(change[:3])
        if change[3] is None:
            cells.pop(pos, None)
        elif type(change[3]) is int:
            cells[pos] = change[3]
        else:
            raise ContractError(f"{where}.changes[{i}]: cell must be integer or null")


def _translated(cells: dict[tuple[int, int, int], int], dx: int) -> dict[tuple[int, int, int], int]:
    return {(p[0] + dx, p[1], p[2]): c for p, c in cells.items()}


class CaseChecker:
    """Incremental trace checker; consumes one tick and retains only current state."""

    def __init__(self, contract: Contract, trace: dict[str, Any]):
        self.contract = contract
        self.initial_cells, self.initial_owners = _parse_initial(trace)
        self.cells = dict(self.initial_cells)
        self.owners = self.initial_owners
        self.id_origins = tuple(sorted(p for p, c in self.cells.items() if (c & 15) != ARMS_KIND))
        self.id_kinds = tuple(self.initial_cells[p] & 15 for p in self.id_origins)
        self.ids = {i: p for i, p in enumerate(self.id_origins)}
        if contract.recurrence == "bounded":
            assert contract.boundary_envelope is not None
            lower, upper = contract.boundary_envelope
            for pos in self.id_origins:
                if any(pos[i] < lower[i] or pos[i] > upper[i] for i in range(3)):
                    raise ContractError(f"initial permanent identity at {pos} is outside boundary_envelope")
        self.port_ids: dict[str, int] = {}
        self.port_motion_prefix: dict[str, tuple[int, tuple[int, ...]]] = {}
        for port in contract.ports:
            identity = next((i for i, pos in self.ids.items() if pos == port.at), None)
            if identity is None:
                raise ContractError(f"port {port.name}: no permanent block at {port.at}")
            self.port_ids[port.name] = identity
            prefix = [0]
            for char in port.word:
                prefix.append(prefix[-1] + (char == "m"))
            self.port_motion_prefix[port.name] = (prefix[-1], tuple(prefix))
        slots = contract.period_ticks // 2
        self.input_max_action_loads = {
            port.name: [None] * slots for port in contract.ports if port.role == "input"
        }
        self.tagged_ids = set(self.port_ids.values())
        self.external_fixtures: dict[tuple[int, int, int], int] = {}
        self.external_arms: dict[tuple[int, int, int], DriveEvent] = {}
        self.whole_assembly_max_action = 0
        self.last_tick = -1
        self.tick_moves: dict[int, tuple[tuple[int, int, int], tuple[int, int, int]]] = {}
        self.tick_actions: dict[int, str] = {}
        self.pending_prescribed: list[dict[str, Any]] = []
        self.prescribed_ids_seen: set[int] = set()
        self.next_prescribed_id = 0

    def validate_prescribed_wrapper(self, wrapper: dict[str, Any], tick: int) -> str | None:
        """Validate injected moves and their session ledger without inferring a natural actuator."""
        if self.contract.prescribed_script is None:
            return "prescribed wrapper received without a declared prescribed_script"
        if set(wrapper) != {"tick", "prescribed_order", "pending_before", "pending_after", "trace"}:
            return f"tick {tick}: malformed prescribed wrapper fields {sorted(wrapper)}"
        if wrapper.get("tick") != tick:
            return f"tick {tick}: prescribed wrapper tick mismatch: {wrapper.get('tick')}"
        if wrapper.get("prescribed_order") != self.contract.prescribed_order:
            return f"tick {tick}: prescribed_order differs from contract"
        before = self._pending_record(self.pending_prescribed)
        try:
            actual_before = self._parse_pending(wrapper.get("pending_before"), "pending_before")
        except ContractError as exc:
            return f"tick {tick}: {exc}"
        if actual_before != self._parse_pending(before, "ledger_before"):
            return f"tick {tick}: pending_before differs from prior prescribed ledger; expected {before}, actual {wrapper.get('pending_before')}"
        starts = [event for event in self.contract.prescribed if event.tick == tick]
        settles = [event for event in self.contract.prescribed if event.tick + 1 == tick]
        expected_before = self.pending_prescribed
        if (starts and expected_before) or (settles and len(settles) != len(expected_before)) or \
                (expected_before and not settles) or (settles and not expected_before):
            return f"tick {tick}: prescribed script has overlapping or unmatched lifecycle"
        trace = wrapper.get("trace")
        if not isinstance(trace, dict) or not isinstance(trace.get("steps"), list):
            return f"tick {tick}: prescribed trace or steps is malformed"
        prescribed_steps = [step for step in trace["steps"] if isinstance(step, dict) and
                            (step.get("stage") == "prescribed" or
                             str(step.get("action", "")).startswith(("prescribed move", "settle prescribed move")))]
        expected_action_count = len(starts) + len(settles)
        if len(prescribed_steps) != expected_action_count:
            return f"tick {tick}: expected {expected_action_count} prescribed trace action(s), found {len(prescribed_steps)}"
        natural_indices = [index for index, step in enumerate(trace["steps"])
                           if isinstance(step, dict) and step.get("stage") in ("chunk", "piston")]
        if not natural_indices:
            return f"tick {tick}: trace has no natural action-order marker for prescribed ordering"
        next_pending: list[dict[str, Any]] = []
        moving_destinations: set[tuple[int, int, int]] = set()
        next_ids_seen = set(self.prescribed_ids_seen)
        next_id = self.next_prescribed_id
        if starts:
            for event, step in zip(starts, prescribed_steps):
                step_index = trace["steps"].index(step)
                if self.contract.prescribed_order == "before_natural" and step_index >= min(natural_indices):
                    return f"tick {tick}: prescribed start did not occur before natural processing"
                if self.contract.prescribed_order == "after_natural" and step_index <= max(natural_indices):
                    return f"tick {tick}: prescribed start did not occur after natural processing"
                if step.get("action") != "prescribed move":
                    return f"tick {tick}: prescribed start failed or has unexpected action {step.get('action')}"
                if step.get("active_input") != list(event.input) or step.get("prescribed_order") != self.contract.prescribed_order:
                    return f"tick {tick}: prescribed start input/order does not match script"
                move_id = step.get("prescribed_move_id")
                if type(move_id) is not int or move_id != next_id or move_id in next_ids_seen:
                    return f"tick {tick}: prescribed move id is missing, duplicate, or out of sequence"
                movement = step.get("movement")
                if not isinstance(movement, dict) or movement.get("failure") is not None:
                    return f"tick {tick}: prescribed start has no successful movement overlay"
                sources = movement.get("sources")
                destinations = movement.get("destinations")
                if not isinstance(sources, list) or not isinstance(destinations, list) or not sources:
                    return f"tick {tick}: prescribed movement sources/destinations are malformed"
                try:
                    source_coords = [_coord(pos, "prescribed.sources") for pos in sources]
                    destination_coords = [_coord(pos, "prescribed.destinations") for pos in destinations]
                except ContractError as exc:
                    return f"tick {tick}: {exc}"
                if len(source_coords) != len(destination_coords) or len(set(source_coords)) != len(source_coords):
                    return f"tick {tick}: prescribed movement has unequal or duplicate sources"
                mapping = dict(zip(source_coords, destination_coords))
                if event.input not in mapping or len(source_coords) > event.limit:
                    return f"tick {tick}: prescribed movement omitted input or exceeded max_load {event.limit}"
                if any(dst != (src[0] + 1, src[1], src[2]) for src, dst in mapping.items()):
                    return f"tick {tick}: prescribed movement is not a +X translation"
                closure = set(source_coords) | set(destination_coords)
                if closure & moving_destinations:
                    return f"tick {tick}: prescribed movement closures overlap prior moving destinations"
                # Earlier source cells are vacant and may be reused by a later
                # intent. Only the still-moving destinations remain protected.
                moving_destinations.update(destination_coords)
                next_pending.append({"id": move_id, "input": event.input,
                                     "destinations": tuple(destination_coords)})
                next_ids_seen.add(move_id)
                next_id += 1
        elif settles:
            for pending, event, step in zip(expected_before, settles, prescribed_steps):
                step_index = trace["steps"].index(step)
                if step_index >= min(natural_indices):
                    return f"tick {tick}: prescribed settlement did not occur before natural processing"
                if step.get("action") != "settle prescribed move":
                    return f"tick {tick}: pending prescribed move was not settled"
                if (pending["input"] != event.input or step.get("prescribed_move_id") != pending["id"] or
                        step.get("active_input") != list(pending["input"]) or
                        step.get("prescribed_order") != self.contract.prescribed_order):
                    return f"tick {tick}: settlement does not match pending prescribed move"
                movement = step.get("movement")
                if not isinstance(movement, dict) or movement.get("failure") is not None:
                    return f"tick {tick}: prescribed settlement overlay is malformed"
                try:
                    sources = tuple(_coord(pos, "settlement.sources") for pos in movement.get("sources", []))
                except ContractError as exc:
                    return f"tick {tick}: {exc}"
                if sources != pending["destinations"]:
                    return f"tick {tick}: settlement sources differ from pending destinations"
        after = self._pending_record(next_pending)
        try:
            actual_after = self._parse_pending(wrapper.get("pending_after"), "pending_after")
        except ContractError as exc:
            return f"tick {tick}: {exc}"
        if actual_after != self._parse_pending(after, "ledger_after"):
            return f"tick {tick}: pending_after differs from prescribed lifecycle; expected {after}, actual {wrapper.get('pending_after')}"
        self.pending_prescribed = next_pending
        self.prescribed_ids_seen = next_ids_seen
        self.next_prescribed_id = next_id
        return None

    @staticmethod
    def _pending_record(pending: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [{"id": move["id"], "input": list(move["input"]),
                 "destinations": [list(pos) for pos in move["destinations"]]}
                for move in pending]

    @staticmethod
    def _parse_pending(value: Any, where: str) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            raise ContractError(f"{where}: expected an array of pending moves")
        result = []
        seen_ids: set[int] = set()
        for index, item in enumerate(value):
            if not isinstance(item, dict) or set(item) != {"id", "input", "destinations"}:
                raise ContractError(f"{where}[{index}]: expected id, input, and destinations")
            move_id = _int(item["id"], f"{where}[{index}].id", minimum=0)
            if move_id in seen_ids:
                raise ContractError(f"{where}: duplicate pending move id {move_id}")
            seen_ids.add(move_id)
            input_pos = _coord(item["input"], f"{where}[{index}].input")
            destinations = item["destinations"]
            if not isinstance(destinations, list):
                raise ContractError(f"{where}[{index}].destinations: expected an array")
            parsed = tuple(_coord(pos, f"{where}[{index}].destinations") for pos in destinations)
            if len(set(parsed)) != len(parsed):
                raise ContractError(f"{where}[{index}].destinations: duplicate destination")
            result.append({"id": move_id, "input": input_pos, "destinations": parsed})
        return result

    def prepare_external_before(self, wrapper: dict[str, Any], tick: int) -> str | None:
        """Check and apply exactly the fixture edits declared for this tick."""
        if self.contract.drive_script is None:
            return "fixture wrapper received without a declared drive_script"
        if set(wrapper) != {"tick", "fixture_before", "fixture_after", "trace"}:
            return f"tick {tick}: malformed fixture wrapper fields {sorted(wrapper)}"
        if wrapper.get("tick") != tick:
            return f"fixture wrapper tick mismatch: expected {tick}, actual {wrapper.get('tick')}"
        due_redstone_removals = [event for event in self.contract.drives if event.tick + 2 == tick]
        due_insertions = [event for event in self.contract.drives if event.tick == tick]
        expected_edits = [[*event.redstone, None] for event in due_redstone_removals]
        for event in due_insertions:
            expected_edits.extend(([*event.piston, 9], [*event.redstone, 6]))
        claimed = wrapper.get("fixture_before")
        if claimed != expected_edits:
            return (f"tick {tick}: fixture_before edits differ from drive_script; "
                    f"expected {expected_edits}, actual {claimed}")

        # Verify removals against our own live fixture ledger before applying them.
        for event in due_redstone_removals:
            pos = event.redstone
            if self.external_fixtures.get(pos) != 6 or self.cells.get(pos) != 6:
                return f"tick {tick}: declared redstone cleanup at {pos} has no stationary fixture"
        for event in due_insertions:
            target_id = next((identity for identity in self.port_ids.values()
                              if self.ids[identity] == event.target), None)
            input_port = next((port for port in self.contract.ports
                               if port.role == "input" and self.port_ids[port.name] == target_id), None)
            if input_port is None:
                return f"tick {tick}: drive target {event.target} is not a tagged input port"
            slot = (tick % self.contract.period_ticks) // 2
            if tick % 2 or input_port.word[slot] != "m":
                return f"tick {tick}: drive target {event.target} is not scheduled to move"
            if event.target not in self.cells:
                return f"tick {tick}: drive target contact {event.target} is absent before injection"

        for event in due_redstone_removals:
            self.cells.pop(event.redstone)
            self.external_fixtures.pop(event.redstone, None)
        for event in due_insertions:
            for pos in (event.piston, event.redstone):
                if pos in self.cells:
                    return f"tick {tick}: drive fixture insertion would overwrite occupied cell {pos}"
            self.cells[event.piston] = 9
            self.cells[event.redstone] = 6
            self.external_fixtures[event.piston] = 9
            self.external_fixtures[event.redstone] = 6
        return None

    def finish_external_after(self, wrapper: dict[str, Any], tick: int) -> str | None:
        if self.contract.drive_script is None:
            return "fixture wrapper received without a declared drive_script"
        due_removals = [event for event in self.contract.drives if event.tick + 3 == tick]
        expected_edits = [[*event.piston, None] for event in due_removals]
        claimed = wrapper.get("fixture_after")
        if claimed != expected_edits:
            return (f"tick {tick}: fixture_after edits differ from drive_script; "
                    f"expected {expected_edits}, actual {claimed}")
        due_retractions = [event for event in self.contract.drives if event.tick + 2 == tick]
        for event in due_retractions:
            if event.arm in self.external_arms:
                return f"tick {tick}: external piston at {event.piston} did not remove its arm on retraction"
        for event in due_removals:
            pos = event.piston
            if self.external_fixtures.get(pos) != 9 or self.cells.get(pos) != 9:
                return f"tick {tick}: piston cleanup at {pos} requires ordinary reset state 0"
            if (pos[0] + 1, pos[1], pos[2]) in self.cells and \
                    (self.cells[(pos[0] + 1, pos[1], pos[2])] & 15) == ARMS_KIND:
                return f"tick {tick}: piston cleanup at {pos} found a remaining piston arm"
            if any(owner == pos for owner, _ in self.owners):
                return f"tick {tick}: piston cleanup at {pos} found a nonempty piston list"
            self.cells.pop(pos)
            self.external_fixtures.pop(pos, None)
        if (tick + 1) % self.contract.period_ticks == 0 and self.external_fixtures:
            return f"tick {tick}: external drive fixtures remain active at cycle boundary"
        return None

    def _check_active_fixtures(self, tick: int) -> str | None:
        for pos, kind in self.external_fixtures.items():
            cell = self.cells.get(pos)
            if cell is None or cell & 15 != kind:
                return f"tick {tick}: external fixture at {pos} moved or changed kind"
            if cell & 16:
                return f"tick {tick}: external fixture at {pos} became moving"
            if kind == 9 and ((cell >> 5) & 7) != 0:
                return f"tick {tick}: external piston at {pos} changed facing"
        for pos in self.external_arms:
            if self.cells.get(pos) != ARMS_KIND:
                return f"tick {tick}: external piston arm at {pos} moved or changed kind"

    def consume(self, trace: dict[str, Any], expected_tick: int, *,
                defer_recurrence: bool = False) -> str | None:
        if not isinstance(trace, dict):
            return f"tick {expected_tick}: trace row is not an object"
        # The driver output for each tick repeats its pre-tick snapshot. Check it
        # against the prior streamed final state so truncated or reordered lines fail.
        incoming, incoming_owners = _parse_initial(trace)
        if incoming != self.cells or incoming_owners != self.owners:
            return f"tick {expected_tick}: trace initial state does not match previous tick final state"
        tick_moves: dict[int, tuple[tuple[int, int, int], tuple[int, int, int]]] = {}
        tick_actions: dict[int, str] = {}
        drive_matches = {i: 0 for i, event in enumerate(self.contract.drives)
                         if event.tick == expected_tick}
        steps = trace.get("steps")
        if not isinstance(steps, list):
            return f"tick {expected_tick}: steps is not an array"
        if not steps:
            return f"tick {expected_tick}: trace has no step timestamps"
        for si, step in enumerate(steps):
            if not isinstance(step, dict):
                return f"tick {expected_tick}: step {si} is malformed"
            if step.get("tick") != expected_tick:
                return f"trace step tick mismatch: expected {expected_tick}, actual {step.get('tick')}"
            action = step.get("action")
            movement = step.get("movement")
            if isinstance(movement, dict) and action != "settle prescribed move":
                failure = movement.get("failure")
                if failure is not None:
                    actor = step.get("active_piston")
                    return (f"tick {expected_tick}: movement failed at actor {actor}: "
                            f"{failure.get('reason', 'unknown reason')} at {failure.get('pos')}")
                sources, destinations = movement.get("sources"), movement.get("destinations")
                if sources is not None and destinations is not None:
                    if len(sources) != len(destinations):
                        return f"tick {expected_tick}: action {action} has unequal source/destination counts"
                    mapping = {tuple(src): tuple(dst) for src, dst in zip(sources, destinations)}
                    if len(mapping) != len(sources):
                        return f"tick {expected_tick}: action {action} repeats a movement source"
                    moved_external = (set(mapping) & self.external_fixtures.keys()) | \
                        (set(mapping) & self.external_arms.keys())
                    if action in ("extend", "retract") and moved_external:
                        return f"tick {expected_tick}: action {action} moved external fixture source(s) {sorted(moved_external)}"
                    if action in ("extend", "retract", "prescribed move"):
                        # Keep identity moves simultaneous, allowing adjacent same-kind blocks.
                        this_action_ids: set[int] = set()
                        for identity, pos in list(self.ids.items()):
                            if pos in mapping:
                                if identity in self.tagged_ids and identity in tick_moves:
                                    return (f"tick {expected_tick}: tagged identity {identity} at {pos} "
                                            "moved more than once")
                                destination = mapping[pos]
                                tick_moves[identity] = (pos, destination)
                                tick_actions[identity] = str(action)
                                this_action_ids.add(identity)
                                self.ids[identity] = destination
                        source_count = len(sources)
                        self.whole_assembly_max_action = max(self.whole_assembly_max_action,
                                                             source_count)
                        slot = (expected_tick % self.contract.period_ticks) // 2
                        actor = step.get("active_piston")
                        for drive_index, event in enumerate(self.contract.drives):
                            if event.tick == expected_tick and actor == list(event.piston):
                                if action != "extend":
                                    return f"tick {expected_tick}: external drive actor {actor} did not extend"
                                if event.target not in mapping:
                                    # The declared contact must be a source in this exact action.
                                    return f"tick {expected_tick}: drive actor {actor} did not move target {event.target}"
                                if len(sources) > event.limit:
                                    return (f"tick {expected_tick}: external drive at {actor} moved "
                                            f"{len(sources)} sources, cap {event.limit}")
                                delta_target = mapping.get(event.target)
                                expected_target = (event.target[0] + 1, event.target[1], event.target[2])
                                if delta_target != expected_target:
                                    return (f"tick {expected_tick}: external drive target expected destination "
                                                f"{expected_target}, actual {delta_target}")
                                drive_matches[drive_index] += 1
                                if event.arm in self.external_arms:
                                    return f"tick {expected_tick}: drive arm site {event.arm} is already active"
                                self.external_arms[event.arm] = event
                        for port in self.contract.ports:
                            identity = self.port_ids[port.name]
                            if identity in this_action_ids and port.role == "input":
                                observed = self.input_max_action_loads[port.name][slot]
                                self.input_max_action_loads[port.name][slot] = (
                                    source_count if observed is None else max(observed, source_count))
                                bound_base = port.baseline[slot] if port.baseline else None
                                bound_spare = port.spare[slot] if port.spare else 0
                                if bound_base is not None:
                                    total = source_count
                                    allowed = bound_base + (bound_spare or 0)
                                    if total > allowed:
                                        return (f"tick {expected_tick}: input {port.name} load budget exceeded; "
                                                f"action {action} moved {total} sources, baseline {bound_base} "
                                                f"+ spare {bound_spare or 0} = {allowed}; "
                                                f"actor={step.get('active_piston')}")
                        if action == "prescribed move":
                            event = next((event for event in self.contract.prescribed
                                          if event.tick == expected_tick), None)
                            if event is None:
                                return f"tick {expected_tick}: undeclared prescribed move action"
                            if len(sources) > event.limit:
                                return (f"tick {expected_tick}: prescribed move moved {len(sources)} sources, "
                                        f"max_load {event.limit}")
            _apply_changes(self.cells, step.get("changes"), f"tick {expected_tick} step {si}")
            for arm, event in list(self.external_arms.items()):
                cell = self.cells.get(arm)
                if cell != ARMS_KIND:
                    if cell is None and expected_tick == event.tick + 2:
                        self.external_arms.pop(arm, None)
                    else:
                        return (f"tick {expected_tick}: external piston arm at {arm} disappeared or changed "
                                f"outside its scheduled retraction (expected tick {event.tick + 2})")
            owners = step.get("owners", [])
            try:
                self.owners = tuple(sorted((_coord(p[0], "owner"), _coord(p[1], "member")) for p in owners))
            except (TypeError, IndexError) as exc:
                return f"tick {expected_tick}: malformed owner snapshot: {exc}"

            occupied_ids = set()
            for identity, pos in self.ids.items():
                cell = self.cells.get(pos)
                if cell is None:
                    return f"tick {expected_tick}: permanent identity {identity} deleted at {pos}"
                original = self.id_kinds[identity]
                if (cell & 15) != original:
                    return f"tick {expected_tick}: permanent identity {identity} replaced at {pos}"
                if pos in occupied_ids:
                    return f"tick {expected_tick}: two permanent identities occupy {pos}"
                occupied_ids.add(pos)
            for pos, cell in self.cells.items():
                if ((cell & 15) != ARMS_KIND and pos not in occupied_ids
                        and self.external_fixtures.get(pos) != (cell & 15)):
                    return f"tick {expected_tick}: new or replacement permanent block at {pos}"
            fixture_error = self._check_active_fixtures(expected_tick)
            if fixture_error:
                return fixture_error
        if any(count != 1 for count in drive_matches.values()):
            missing = [self.contract.drives[i].piston for i, count in drive_matches.items() if count != 1]
            return f"tick {expected_tick}: external drive action missing or repeated for actor(s) {missing}"
        self.tick_moves = tick_moves
        self.tick_actions = tick_actions
        self.last_tick = expected_tick
        message = self._check_ports(expected_tick, tick_moves, tick_actions)
        if message:
            return message
        if not defer_recurrence:
            return self.check_boundary(expected_tick)
        return None

    def check_boundary(self, expected_tick: int) -> str | None:
        if (expected_tick + 1) % self.contract.period_ticks == 0:
            cycles = (expected_tick + 1) // self.contract.period_ticks
            if self.contract.recurrence == "exact":
                expected = _translated(self.initial_cells, self.contract.advance * cycles)
                dx = self.contract.advance * cycles
                translate = lambda p: (p[0] + dx, p[1], p[2])
                expected_owners = tuple(sorted((translate(owner), translate(member))
                                               for owner, member in self.initial_owners))
                if self.cells != expected:
                    return f"tick {expected_tick}: recurrence mismatch at cycle {cycles} boundary"
                if self.owners != expected_owners:
                    return f"tick {expected_tick}: piston owner recurrence mismatch at cycle {cycles} boundary"
            else:
                assert self.contract.boundary_envelope is not None
                lower, upper = self.contract.boundary_envelope
                dx = self.contract.advance * cycles
                shifted_lower = (lower[0] + dx, lower[1], lower[2])
                shifted_upper = (upper[0] + dx, upper[1], upper[2])
                for identity, pos in self.ids.items():
                    if any(pos[i] < shifted_lower[i] or pos[i] > shifted_upper[i] for i in range(3)):
                        return (f"tick {expected_tick}: permanent identity {identity} at {pos} is outside "
                                f"translated boundary_envelope {shifted_lower}..{shifted_upper}")
        return None

    def _check_ports(self, tick: int,
                     tick_moves: dict[int, tuple[tuple[int, int, int], tuple[int, int, int]]],
                     tick_actions: dict[int, str]) -> str | None:
        slot = (tick % self.contract.period_ticks) // 2
        for port in self.contract.ports:
            ident = self.port_ids[port.name]
            moved = ident in tick_moves
            char = port.word[slot]
            is_move_tick = tick % 2 == 0
            should_move = is_move_tick and char == "m"
            if moved != should_move:
                expected = "move +X" if should_move else "wait"
                actual = "moved" if moved else "did not move"
                moved_ids = sorted(tick_moves)
                actions = sorted(set(tick_actions.values()))
                detail = f"action={','.join(actions) or 'none'} moved_ids={moved_ids}"
                return f"tick {tick}: port {port.name} expected {expected}, actual {actual}; {detail}"
            pos = self.ids[ident]
            origin = self.id_origins[ident]
            complete_cycles, rem = divmod(tick, self.contract.period_ticks)
            completed_slots = rem // 2 + 1
            total_moves, prefix = self.port_motion_prefix[port.name]
            moved_count = complete_cycles * total_moves + prefix[completed_slots]
            expected = (origin[0] + moved_count, origin[1], origin[2])
            if pos != expected:
                moved_ids = sorted(tick_moves)
                actions = sorted(set(tick_actions.values()))
                detail = f"action={','.join(actions) or 'none'} moved_ids={moved_ids}"
                return (f"tick {tick}: port {port.name} expected position {expected}, "
                        f"actual {pos}; {detail}")
            cell = self.cells.get(pos)
            moving = bool(cell is not None and cell & 16)
            expected_moving = should_move
            if moving != expected_moving:
                moved_ids = sorted(tick_moves)
                actions = sorted(set(tick_actions.values()))
                detail = f"action={','.join(actions) or 'none'} moved_ids={moved_ids}"
                return (f"tick {tick}: port {port.name} expected moving={expected_moving}, "
                        f"actual moving={moving}; {detail}")
        return None


def _validate_word_motion(contract: Contract) -> str | None:
    for port in contract.ports:
        if port.word.count("m") != contract.advance:
            return f"port {port.name}: word has {port.word.count('m')} moves, expected advance {contract.advance}"
    return None


def _driver_path(external: bool = False) -> Path:
    stem = "extension-drive" if external else "extension-trace"
    names = (f"{stem}.exe", stem) if os.name == "nt" else (stem, f"{stem}.exe")
    for name in names:
        candidate = ROOT / "target" / "release" / name
        if candidate.is_file():
            return candidate
    raise ContractError(f"{stem} executable not found under target/release")


def _prescribed_driver_path() -> Path:
    for name in ("extension-prescribe.exe", "extension-prescribe") if os.name == "nt" else ("extension-prescribe", "extension-prescribe.exe"):
        candidate = ROOT / "target" / "release" / name
        if candidate.is_file():
            return candidate
    raise ContractError("extension-prescribe executable not found under target/release")


def _flyer_initial_trace(flyer_path: Path) -> dict[str, Any]:
    """Build the trusted pre-injection state from the public Python API."""
    from fastflyer import Flyer

    flyer = Flyer.load(flyer_path)
    blocks = list(flyer.blocks())
    owners = sorted((owner, member) for owner, block in blocks
                    if block.kind.name == "PISTON"
                    for member in flyer.get_piston_blocks(owner))
    return {
        "initial": [[*pos, block.encode()] for pos, block in blocks],
        "initial_owners": [[list(owner), list(member)] for owner, member in owners],
        "steps": [],
    }


def run_case(contract: Contract, driver: Path, sample: tuple[int, int, int] | None) -> dict[str, Any]:
    started = time.perf_counter()
    rng, px, pz = sample if sample is not None else (None, None, None)
    args = [str(driver), str(contract.flyer), str(contract.period_ticks * contract.cycles)]
    if contract.drive_script is not None:
        args.append(str(contract.drive_script))
    if contract.prescribed_script is not None:
        args.extend((str(contract.prescribed_script),
                     "before" if contract.prescribed_order == "before_natural" else "after"))
    if sample is not None:
        args.extend(map(str, sample))
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                               encoding="utf-8", errors="replace", bufsize=1)
    checker: CaseChecker | None = None
    failure: str | None = None
    tick_count = 0
    try:
        try:
            checker = CaseChecker(contract, _flyer_initial_trace(contract.flyer))
        except Exception as exc:
            failure = f"tick 0: cannot initialize contract checker from Flyer.load: {exc}"
        assert process.stdout is not None
        for line_no, line in enumerate(process.stdout, 1):
            if failure:
                break
            try:
                output = json.loads(line)
            except json.JSONDecodeError as exc:
                failure = f"driver output line {line_no}: invalid JSON: {exc}"
                break
            assert checker is not None
            try:
                if contract.prescribed_script is not None:
                    if not isinstance(output, dict):
                        failure = f"tick {tick_count}: prescribed wrapper is not an object"
                    else:
                        failure = checker.validate_prescribed_wrapper(output, tick_count)
                        if failure is None:
                            failure = checker.consume(output.get("trace"), tick_count,
                                                      defer_recurrence=True)
                        if failure is None:
                            if (tick_count + 1) % contract.period_ticks == 0 and checker.pending_prescribed:
                                failure = f"tick {tick_count}: prescribed move remains pending at period boundary"
                            else:
                                failure = checker.check_boundary(tick_count)
                elif contract.drive_script is None:
                    failure = checker.consume(output, tick_count)
                elif not isinstance(output, dict):
                    failure = f"tick {tick_count}: fixture wrapper is not an object"
                else:
                    failure = checker.prepare_external_before(output, tick_count)
                    if failure is None:
                        failure = checker.consume(output.get("trace"), tick_count,
                                                  defer_recurrence=True)
                    if failure is None:
                        failure = checker.finish_external_after(output, tick_count)
                    if failure is None:
                        failure = checker.check_boundary(tick_count)
            except (ContractError, TypeError, ValueError, KeyError) as exc:
                failure = f"tick {tick_count}: malformed trace: {exc}"
            tick_count += 1
            if failure:
                break
        if failure:
            process.terminate()
        remaining, err = process.communicate(timeout=5)
        if process.returncode not in (0, None) and not failure:
            failure = f"driver exited with status {process.returncode}: {err.strip()}"
        elif tick_count != contract.period_ticks * contract.cycles and not failure:
            failure = f"driver emitted {tick_count} ticks; expected {contract.period_ticks * contract.cycles}"
        if not failure and checker is not None:
            for port in contract.ports:
                if checker.ids[checker.port_ids[port.name]][0] - port.at[0] != contract.advance * contract.cycles:
                    failure = f"port {port.name}: final X displacement does not equal total advance"
                    break
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
    input_loads = checker.input_max_action_loads if checker is not None else {}
    whole_max = checker.whole_assembly_max_action if checker is not None else 0
    return {"rng": rng, "phase_x": px, "phase_z": pz, "passed": failure is None,
            "ticks": tick_count, "elapsed_seconds": round(time.perf_counter() - started, 6),
            "diagnostic": failure, "input_max_action_loads": input_loads,
            "whole_assembly_max_action": whole_max}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--samples", action="store_true", help="run 80 RNG/phase combinations")
    parser.add_argument("--out", type=Path, help="write machine-readable result JSON")
    parser.add_argument("--driver", type=Path, help="path to extension trace/drive executable")
    args = parser.parse_args(argv)
    try:
        contract = load_contract(args.contract.resolve())
        motion_error = _validate_word_motion(contract)
        if motion_error:
            raise ContractError(motion_error)
        if not contract.flyer.is_file():
            raise ContractError(f"fixture does not exist: {contract.flyer}")
        driver = args.driver.resolve() if args.driver else (
            _prescribed_driver_path() if contract.prescribed_script is not None else
            _driver_path(contract.drive_script is not None))
        cases = [run_case(contract, driver, sample) for sample in (SAMPLES if args.samples else [None])]
        result = {"version": 1, "name": contract.name, "period_ticks": contract.period_ticks,
                  "advance": contract.advance, "cycles": contract.cycles,
                  "recurrence": contract.recurrence,
                  "drive_script": (str(contract.drive_script) if contract.drive_script else None),
                  "prescribed_script": (str(contract.prescribed_script) if contract.prescribed_script else None),
                  "prescribed_order": contract.prescribed_order,
                  "boundary_envelope": ({"min": contract.boundary_envelope[0],
                                         "max": contract.boundary_envelope[1]}
                                        if contract.boundary_envelope else None),
                  "passed": all(case["passed"] for case in cases), "cases": cases}
        if contract.prescribed_script is not None:
            result["claim"] = (f"prescribed input injection ({contract.prescribed_order}); "
                               "validated start/settlement ledger + sampled ports + candidate-state recurrence; "
                               "does not establish natural driver realization")
        elif contract.drive_script is not None:
            result["claim"] = ("externally driven fixture; sampled ports + bounded hardware; "
                               "no exact-state recurrence claim"
                               if contract.recurrence == "bounded" else
                               "externally driven fixture; sampled ports + exact translated candidate-state recurrence")
        else:
            result["claim"] = ("sampled ports + bounded hardware; no exact-state recurrence claim"
                               if contract.recurrence == "bounded" else
                               "sampled ports + exact translated state recurrence")
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        elapsed = sum(case["elapsed_seconds"] for case in cases)
        if args.samples:
            passed = sum(case["passed"] for case in cases)
            first_failure = next((case for case in cases if not case["passed"]), None)
            if first_failure is None:
                print(f"{contract.name}: PASS ({passed}/{len(cases)} samples; {elapsed:.2f}s; {result['claim']})")
            else:
                label = f"rng={first_failure['rng']} phases=({first_failure['phase_x']},{first_failure['phase_z']})"
                print(f"{contract.name}: FAIL ({passed}/{len(cases)} samples; first failure {label}: "
                      f"{first_failure['diagnostic']}; {result['claim']})")
        else:
            case = cases[0]
            details = (f"whole max action={case['whole_assembly_max_action']}; "
                       f"input max loads={case['input_max_action_loads']}")
            print(f"{contract.name}: {'PASS' if result['passed'] else 'FAIL'} ({elapsed:.2f}s; "
                  f"{result['claim']}; {details})"
                  + (f" — {case['diagnostic']}" if case["diagnostic"] else ""))
        return 0 if result["passed"] else 1
    except ContractError as exc:
        print(f"contract error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
