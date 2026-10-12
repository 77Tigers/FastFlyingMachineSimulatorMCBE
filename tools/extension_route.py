"""Necessary connected-glue bound for two periodic contact cells.

This is a 6-face lattice path check. It does not model power, piston states,
adhesion, arms, or full Flyer movement legality.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any


class RouteError(ValueError):
    """Invalid two-contact route request."""


def _integer(value: Any, where: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RouteError(f"{where} must be an integer")
    if minimum is not None and value < minimum:
        raise RouteError(f"{where} must be at least {minimum}")
    return value


def _position(value: Any, where: str) -> tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3:
        raise RouteError(f"{where} must be an [x, y, z] integer triple")
    return tuple(_integer(c, f"{where}[{i}]") for i, c in enumerate(value))  # type: ignore[return-value]


def _word(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value or any(c not in "mw" for c in value):
        raise RouteError(f"{where} must be a non-empty word containing only 'm' and 'w'")
    return value


def _validate(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise RouteError("request must be a JSON object")
    required = {"version", "name", "target_word", "contacts", "blockers", "reserved", "glue_budget"}
    if request.keys() != required:
        missing, extra = required - request.keys(), request.keys() - required
        if missing:
            raise RouteError(f"missing field(s): {', '.join(sorted(missing))}")
        raise RouteError(f"unknown field(s): {', '.join(sorted(extra))}")
    if _integer(request["version"], "version") != 1:
        raise RouteError("version must be 1")
    name = request["name"]
    if not isinstance(name, str) or not name:
        raise RouteError("name must be a non-empty string")
    target = _word(request["target_word"], "target_word")
    budget = _integer(request["glue_budget"], "glue_budget", 1)
    contacts = request["contacts"]
    if not isinstance(contacts, list) or len(contacts) != 2:
        raise RouteError("contacts must contain exactly two coordinates")
    contacts = [_position(p, f"contacts[{i}]") for i, p in enumerate(contacts)]
    if contacts[0] == contacts[1]:
        raise RouteError("contact coordinates must be distinct")
    blockers = request["blockers"]
    if not isinstance(blockers, list):
        raise RouteError("blockers must be an array")
    parsed_blockers = []
    target_advance = target.count("m")
    for i, blocker in enumerate(blockers):
        where = f"blockers[{i}]"
        if not isinstance(blocker, dict) or blocker.keys() != {"word", "cells"}:
            raise RouteError(f"{where} must contain exactly 'word' and 'cells'")
        word = _word(blocker["word"], f"{where}.word")
        if len(word) != len(target) or word.count("m") != target_advance:
            raise RouteError(f"{where}.word must have the target period and advance")
        if not isinstance(blocker["cells"], list):
            raise RouteError(f"{where}.cells must be an array")
        cells = [_position(p, f"{where}.cells[{j}]") for j, p in enumerate(blocker["cells"])]
        if not cells or len(set(cells)) != len(cells):
            raise RouteError(f"{where}.cells must be non-empty and unique")
        parsed_blockers.append({"word": word, "cells": cells})
    reserved = request["reserved"]
    if not isinstance(reserved, list):
        raise RouteError("reserved must be an array")
    reserved = [_position(p, f"reserved[{i}]") for i, p in enumerate(reserved)]
    if len(set(reserved)) != len(reserved):
        raise RouteError("reserved coordinates must be unique")
    if set(contacts) & set(reserved):
        raise RouteError("contacts overlap reserved non-glue cells")

    forbidden = set(reserved)
    for blocker in parsed_blockers:
        for slot in range(len(target)):
            delta = blocker["word"].count("m", 0, slot) - target.count("m", 0, slot)
            forbidden.update((x + delta, y, z) for x, y, z in blocker["cells"])
    if set(contacts) & forbidden:
        raise RouteError("contacts overlap a forbidden blocker or reserved cell")
    return {"name": name, "target_word": target, "contacts": contacts,
            "forbidden": forbidden, "glue_budget": budget}


_STEPS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def _bfs(start: tuple[int, int, int], goal: tuple[int, int, int], forbidden: set[tuple[int, int, int]],
         max_edges: int, max_nodes: int):
    queue = deque([start])
    previous: dict[tuple[int, int, int], tuple[int, int, int] | None] = {start: None}
    distance = {start: 0}
    while queue:
        point = queue.popleft()
        depth = distance[point]
        if point == goal:
            path = []
            while point is not None:
                path.append(point)
                point = previous[point]
            return path[::-1], len(distance), False
        if depth >= max_edges:
            continue
        for step in _STEPS:
            nxt = tuple(point[i] + step[i] for i in range(3))
            if nxt in forbidden or nxt in distance:
                continue
            if len(distance) >= max_nodes:
                return None, len(distance), True
            previous[nxt] = point
            distance[nxt] = depth + 1
            queue.append(nxt)
    return None, len(distance), False


def check_route(request: Any, *, search_depth: int | None = None,
                max_nodes: int = 250_000) -> dict[str, Any]:
    """Prove a budget bound and optionally find the shortest path to a depth cap.

    search_depth counts glue cells including both contacts. No artificial box is
    imposed; finite BFS depth and max_nodes bound the computation.
    """
    checked = _validate(request)
    budget = checked["glue_budget"]
    if search_depth is None:
        search_depth = budget
    _integer(search_depth, "search_depth", budget)
    _integer(max_nodes, "max_nodes", 1)
    start, goal = checked["contacts"]
    # Finish the finite budget frontier first so a later cap cannot erase its proof.
    path, visited, capped = _bfs(start, goal, checked["forbidden"], budget - 1, max_nodes)
    if path is not None:
        return {
            "verdict": "within_budget", "name": checked["name"], "glue_budget": budget,
            "required_glue": len(path), "required_glue_exact": True,
            "path": [list(p) for p in path],
            "forbidden_count": len(checked["forbidden"]),
            "search": {"status": "shortest_path_found", "depth_limit": budget,
                       "visited": visited, "node_cap": max_nodes},
            "physical_obligations": "unresolved: power, piston states, arms, adhesion recruitment, and full movement checks are outside this bound",
        }
    if capped:
        verdict, status = "unknown", "node_cap_before_budget_proof"
    else:
        verdict, status = "over_budget", "budget_excluded"
    if verdict == "unknown" or search_depth == budget:
        return {
            "verdict": verdict, "name": checked["name"], "glue_budget": budget,
            "required_glue": budget + 1 if verdict == "over_budget" else None,
            "required_glue_exact": False, "path": None, "forbidden_count": len(checked["forbidden"]),
            "search": {"status": status, "depth_limit": budget,
                       "visited": visited, "node_cap": max_nodes},
            "physical_obligations": "unresolved: power, piston states, arms, adhesion recruitment, and full movement checks are outside this bound",
        }
    path, optional_visited, optional_capped = _bfs(
        start, goal, checked["forbidden"], search_depth - 1, max_nodes
    )
    if path is not None:
        required = len(path)
        status = "shortest_path_found"
    else:
        required = budget + 1
        status = "budget_excluded_optional_search_capped" if optional_capped else "budget_excluded_no_path_to_depth_limit"
    return {
        "verdict": "over_budget", "name": checked["name"], "glue_budget": budget,
        "required_glue": required, "required_glue_exact": path is not None,
        "path": [list(p) for p in path] if path else None,
        "forbidden_count": len(checked["forbidden"]),
        "search": {"status": status, "depth_limit": search_depth,
                   "visited": optional_visited, "node_cap": max_nodes},
        "physical_obligations": "unresolved: power, piston states, arms, adhesion recruitment, and full movement checks are outside this bound",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bound connected glue needed between two periodic contacts")
    parser.add_argument("request", type=Path, help="version-1 route request JSON")
    parser.add_argument("--search-depth", type=int, help="maximum glue cells to search; defaults to budget")
    parser.add_argument("--max-nodes", type=int, default=250_000, help="visited-cell guard")
    parser.add_argument("--out", type=Path, help="write machine-readable result JSON")
    args = parser.parse_args(argv)
    try:
        request = json.loads(args.request.read_text(encoding="utf-8"))
        result = check_route(request, search_depth=args.search_depth, max_nodes=args.max_nodes)
    except (OSError, json.JSONDecodeError, RouteError) as error:
        print(f"invalid route request: {error}", file=sys.stderr)
        return 2
    encoded = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if result["verdict"] != "unknown" else 3


if __name__ == "__main__":
    raise SystemExit(main())
