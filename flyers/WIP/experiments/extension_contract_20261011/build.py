"""Build deterministic extension-contract fixtures from the bank 3bps driver.

Run from any directory with ``python path/to/build.py``. The script saves and
reloads flyers before defining ports, then derives all port words and loads
from the real Rust extension-trace executable.
"""

from __future__ import annotations

import json
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))

from fastflyer import Block, Flyer, Kind


OUT = HERE / "out"
BENCH = HERE / "benchmarks"
REFERENCE_SOURCE = REPO / "flyers/bank/pl12/human_tm_smol_3bps.flyer"
TRACE_EXE = REPO / "target/release" / ("extension-trace.exe" if os.name == "nt" else "extension-trace")
TICKS = 30
SEED = 5
PHASE_X = 0
PHASE_Z = 0
INPUT_AT = (13, 4, 7)
OUTPUT_AT = (7, 1, 4)
WRONG_PHASE_WORD = "wmmmw"
PAYLOAD_OFFSETS = ((0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1))
BOUNDARY_ENVELOPE = {"min": [0, 0, 1], "max": [17, 7, 9]}


def ensure_trace_executable() -> None:
    if TRACE_EXE.exists():
        return
    subprocess.run(
        [
            "cargo",
            "build",
            "--release",
            "--manifest-path",
            str(REPO / "tools/Cargo.toml"),
            "--target-dir",
            str(REPO / "target"),
            "--bin",
            "extension-trace",
        ],
        cwd=REPO,
        check=True,
    )
    if not TRACE_EXE.exists():
        raise RuntimeError(f"trace executable was not produced: {TRACE_EXE}")


def trace(path: Path) -> list[dict[str, Any]]:
    result = subprocess.run(
        [str(TRACE_EXE), str(path), str(TICKS), str(SEED), str(PHASE_X), str(PHASE_Z)],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    )
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]


def port_events(
    traces: list[dict[str, Any]], starts: list[tuple[int, int, int]]
) -> tuple[dict[tuple[int, int, int], list[dict[str, Any]]], list[dict[str, Any]]]:
    """Track each initial block through successful actions via source/dest pairs."""
    positions = {start: start for start in starts}
    events = {start: [] for start in starts}
    failures = []
    for tick, trace_tick in enumerate(traces):
        for step in trace_tick["steps"]:
            movement = step.get("movement") or {}
            if movement.get("failure"):
                failures.append(
                    {"tick": tick, "action": step.get("action"),
                     "piston": step.get("active_piston"),
                     "failure": movement["failure"]}
                )
            if not step.get("action"):
                continue
            sources = movement.get("sources") or []
            destinations = movement.get("destinations") or []
            if len(sources) != len(destinations):
                continue
            # Snapshot before applying mappings so simultaneous adjacent blocks
            # cannot claim another tracker's newly assigned destination.
            changes = []
            for origin, position in positions.items():
                try:
                    index = sources.index(list(position))
                except ValueError:
                    continue
                events[origin].append(
                    {"tick": tick, "action": step["action"],
                     "load": len(sources), "piston": step.get("active_piston")}
                )
                changes.append((origin, tuple(destinations[index])))
            for origin, destination in changes:
                positions[origin] = destination
    return events, failures


def summarized_port(
    events: list[dict[str, Any]], *, cycles: int = 3
) -> tuple[str, list[int | None], list[list[dict[str, Any]]]]:
    by_slot: list[list[list[dict[str, Any]]]] = [[] for _ in range(5)]
    for cycle in range(cycles):
        cycle_slots: list[list[dict[str, Any]]] = [[] for _ in range(5)]
        for event in events:
            if cycle * 10 <= event["tick"] < (cycle + 1) * 10:
                cycle_slots[(event["tick"] % 10) // 2].append(event)
        by_slot = [*by_slot]
        for slot, slot_events in enumerate(cycle_slots):
            by_slot[slot].append(slot_events)

    words = []
    loads: list[int | None] = []
    for slot_cycles in by_slot:
        present = [bool(cycle_events) for cycle_events in slot_cycles]
        if len(set(present)) != 1:
            raise RuntimeError(f"port recurrence differs across cycles: {slot_cycles}")
        words.append("m" if present[0] else "w")
        if not present[0]:
            loads.append(None)
            continue
        signatures = [tuple((e["action"], e["load"]) for e in cycle_events)
                      for cycle_events in slot_cycles]
        if len(set(signatures)) != 1 or len(signatures[0]) != 1:
            raise RuntimeError(f"port slot does not have one stable stroke: {slot_cycles}")
        loads.append(slot_cycles[0][0]["load"])
    return "".join(words), loads, by_slot


def all_state_boundaries(
    traces: list[dict[str, Any]], envelope: dict[str, list[int]]
) -> list[dict[str, Any]]:
    """Check that every cell and piston owner remains in the translated envelope."""
    state = {tuple(item[:3]): item[3] for item in traces[0]["initial"]}
    owners: list[Any] = traces[0]["initial_owners"]
    snapshots = []
    lo, hi = envelope["min"], envelope["max"]
    for tick, trace_tick in enumerate(traces):
        for step in trace_tick["steps"]:
            for change in step["changes"]:
                position = tuple(change[:3])
                cell = change[3] if len(change) > 3 else None
                if cell is None:
                    state.pop(position, None)
                else:
                    state[position] = cell
            owners = step["owners"]
        boundary = tick + 1
        if boundary not in (10, 20, 30):
            continue
        cycle = boundary // 10
        translated_min = [lo[0] + 3 * cycle, lo[1], lo[2]]
        translated_max = [hi[0] + 3 * cycle, hi[1], hi[2]]
        out_of_bounds = [
            list(position)
            for position in set(state) | {
                tuple(pair[1]) for pair in owners if isinstance(pair, list) and len(pair) == 2
            }
            if any(position[i] < translated_min[i] or position[i] > translated_max[i]
                   for i in range(3))
        ]
        if out_of_bounds:
            raise RuntimeError(
                f"boundary {boundary} has cells/owners outside translated envelope: "
                f"{out_of_bounds[:4]}"
            )
        snapshots.append(
            {"tick": boundary, "cells": len(state), "owners": len(owners),
             "translated_envelope": {"min": translated_min, "max": translated_max}}
        )
    return snapshots


def contract(
    *, name: str, flyer: str,
    input_word: str, input_load: list[int | None], spare_load: list[int | None],
    output_at: tuple[int, int, int], output_word: str,
    side_payload: tuple[int, int, int] | None = None,
) -> dict[str, Any]:
    ports = [
        {"name": "driver_input", "role": "input", "at": list(INPUT_AT),
         "word": input_word, "baseline_load": input_load,
         "spare_load": spare_load},
        {"name": "downstream_output", "role": "output", "at": list(output_at),
         "word": output_word},
    ]
    if side_payload is not None:
        ports.append(
            {"name": "side_payload", "role": "output", "at": list(side_payload),
             "word": input_word}
        )
    return {
        "version": 1,
        "name": name,
        "flyer": flyer,
        "period_ticks": 10,
        "advance": 3,
        "cycles": 3,
        "ports": ports,
        "recurrence": "bounded",
        "boundary_envelope": BOUNDARY_ENVELOPE,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    started = time.perf_counter()
    ensure_trace_executable()
    OUT.mkdir(parents=True, exist_ok=True)
    BENCH.mkdir(parents=True, exist_ok=True)

    # Normalize the bank file through the Python storage API, then reload it
    # before choosing/recording any port coordinates.
    reference_editor = Flyer.load(REFERENCE_SOURCE)
    reference_editor.rng_state = SEED
    reference_editor.phase_x = PHASE_X
    reference_editor.phase_z = PHASE_Z
    reference_path = OUT / "reference.flyer"
    reference_editor.save(reference_path)
    reference = Flyer.load(reference_path)
    if reference.get(INPUT_AT) is None or reference.get(INPUT_AT).kind not in (Kind.SLIME, Kind.HONEY):
        raise RuntimeError(f"saved input coordinate is not glue: {INPUT_AT}")
    if reference.get(OUTPUT_AT) is None or reference.get(OUTPUT_AT).kind not in (Kind.SLIME, Kind.HONEY):
        raise RuntimeError(f"saved output coordinate is not glue: {OUTPUT_AT}")

    reference_traces = trace(reference_path)
    ref_events, ref_failures = port_events(reference_traces, [INPUT_AT, OUTPUT_AT])
    if ref_failures:
        raise RuntimeError(f"reference has failed moves: {ref_failures[:3]}")
    input_word, input_load, input_slots = summarized_port(ref_events[INPUT_AT])
    output_word, output_load, output_slots = summarized_port(ref_events[OUTPUT_AT])
    if input_word != "mmmww" or output_word != "wwmmm":
        raise RuntimeError(f"unexpected reference phases: {input_word=} {output_word=}")

    # Search only transverse, initially exposed faces of the selected input
    # glue. Each candidate is checked by the actual Rust driver for three full
    # cycles, including payload identity, port recurrence, loads and failures.
    payload_path = OUT / "payload.flyer"
    attempts = []
    selected_payload = None
    payload_traces = None
    payload_events = None
    payload_slots = None
    for offset in PAYLOAD_OFFSETS:
        position = tuple(INPUT_AT[i] + offset[i] for i in range(3))
        if reference.get(position) is not None:
            attempts.append({"at": list(position), "result": "occupied"})
            continue
        candidate = Flyer.load(reference_path)
        candidate.set(position, Block(Kind.GLASS))
        candidate.save(payload_path)
        saved_candidate = Flyer.load(payload_path)
        traces = trace(payload_path)
        events, failures = port_events(traces, [INPUT_AT, OUTPUT_AT, position])
        try:
            candidate_input_word, candidate_input_load, _ = summarized_port(events[INPUT_AT])
            candidate_output_word, candidate_output_load, _ = summarized_port(events[OUTPUT_AT])
            payload_word, payload_load, _ = summarized_port(events[position])
        except RuntimeError as exc:
            attempts.append({"at": list(position), "result": "rejected",
                             "reason": str(exc)})
            continue
        expected_schedule = [(e["tick"], e["action"]) for e in ref_events[INPUT_AT]]
        actual_schedule = [(e["tick"], e["action"]) for e in events[INPUT_AT]]
        payload_schedule = [(e["tick"], e["action"]) for e in events[position]]
        output_schedule_ref = [(e["tick"], e["action"]) for e in ref_events[OUTPUT_AT]]
        output_schedule_candidate = [(e["tick"], e["action"]) for e in events[OUTPUT_AT]]
        added_one = all(
            candidate_input_load[i] == input_load[i] + 1
            for i in range(5) if input_load[i] is not None
        )
        same_payload_load = all(
            payload_load[i] == candidate_input_load[i]
            for i in range(5) if candidate_input_load[i] is not None
        )
        accepted = (
            saved_candidate.push_limit == reference.push_limit == 12
            and not failures
            and candidate_input_word == input_word
            and candidate_output_word == output_word
            and payload_word == input_word
            and actual_schedule == expected_schedule == payload_schedule
            and output_schedule_candidate == output_schedule_ref
            and candidate_output_load == output_load
            and added_one
            and same_payload_load
        )
        attempts.append(
            {"at": list(position), "result": "accepted" if accepted else "rejected",
             "failures": len(failures), "input_load": candidate_input_load,
             "payload_word": payload_word}
        )
        if accepted:
            selected_payload = position
            payload_traces = traces
            payload_events = events
            payload_slots = (candidate_input_word, candidate_input_load,
                             candidate_output_word, candidate_output_load)
            break
    if selected_payload is None or payload_traces is None or payload_events is None:
        raise RuntimeError(f"no transverse one-glass candidate passed: {attempts}")

    # Freeze the bounded hardware envelope in the starting world's gauge.
    # The reference driver advances +3 X per 10-tick cycle, so the envelope is
    # translated by 3 at ticks 10/20/30 for boundary occupancy checks.
    reference_boundaries = all_state_boundaries(reference_traces, BOUNDARY_ENVELOPE)
    payload_boundaries = all_state_boundaries(payload_traces, BOUNDARY_ENVELOPE)
    payload_input_load = payload_slots[1]
    payload_output_load = payload_slots[3]
    write_json(
        BENCH / "reference.json",
        contract(name="reference", flyer="../out/reference.flyer",
                 input_word=input_word, input_load=input_load,
                 spare_load=[0 if value is not None else None for value in input_load],
                 output_at=OUTPUT_AT, output_word=output_word),
    )
    write_json(
        BENCH / "payload.json",
        contract(name="payload", flyer="../out/payload.flyer",
                 input_word=input_word, input_load=input_load,
                 spare_load=[1 if value is not None else None for value in input_load],
                 output_at=OUTPUT_AT, output_word=output_word,
                 side_payload=selected_payload),
    )
    write_json(
        BENCH / "wrong_phase.json",
        contract(name="wrong_phase", flyer="../out/reference.flyer",
                 input_word=input_word, input_load=input_load,
                 spare_load=[0 if value is not None else None for value in input_load],
                 output_at=OUTPUT_AT, output_word=WRONG_PHASE_WORD),
    )
    write_json(
        BENCH / "over_budget.json",
        contract(name="over_budget", flyer="../out/payload.flyer",
                 input_word=input_word, input_load=input_load,
                 spare_load=[0 if value is not None else None for value in input_load],
                 output_at=OUTPUT_AT, output_word=output_word,
                 side_payload=selected_payload),
    )

    # Remove the redstone block that directly soft-powers the tick-zero input
    # driver piston. The saved, reachable start is retained; the modified case
    # demonstrates what the real engine does when that source is missing.
    missing_source = Flyer.load(reference_path)
    missing_source.remove((12, 5, 8))
    missing_path = OUT / "missing_source.flyer"
    missing_source.save(missing_path)
    missing_traces = trace(missing_path)
    _, missing_trace_failures = port_events(missing_traces, [INPUT_AT, OUTPUT_AT])
    write_json(
        BENCH / "missing_source.json",
        contract(name="missing_source", flyer="../out/missing_source.flyer",
                 input_word=input_word, input_load=input_load,
                 spare_load=[0 if value is not None else None for value in input_load],
                 output_at=OUTPUT_AT, output_word=output_word),
    )

    summary = {
        "source": "flyers/bank/pl12/human_tm_smol_3bps.flyer",
        "driver": {"rng_state": SEED, "phase_x": PHASE_X, "phase_z": PHASE_Z,
                   "period_ticks": 10, "advance": 3, "cycles": 3},
        "input": {"at": list(INPUT_AT), "kind": "slime", "word": input_word,
                  "baseline_load": input_load},
        "output": {"at": list(OUTPUT_AT), "word": output_word,
                   "baseline_load": output_load},
        "payload": {"at": list(selected_payload), "kind": "glass",
                    "push_limit": reference.push_limit,
                    "candidate_scan_attempts": len(attempts), "scan": attempts,
                    "input_load": payload_input_load,
                    "output_load": payload_output_load},
        "reference_failures": len(ref_failures),
        "payload_failures": 0,
        "reference_boundaries": reference_boundaries,
        "payload_boundaries": payload_boundaries,
        "missing_source": {"removed_redstone_block": [12, 5, 8],
                           "active_tick_zero_piston": [12, 5, 9],
                           "first_trace_failure": (missing_trace_failures[0]
                                                    if missing_trace_failures else None)},
        "trace_executable": str(TRACE_EXE.relative_to(REPO)),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "sha256": {
            "source": hashlib.sha256(REFERENCE_SOURCE.read_bytes()).hexdigest(),
            "reference": hashlib.sha256(reference_path.read_bytes()).hexdigest(),
            "payload": hashlib.sha256(payload_path.read_bytes()).hexdigest(),
        },
    }
    write_json(HERE / "build_summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
