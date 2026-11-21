"""Find the smallest glue set for one body with fixed pistons and power sources.

A cut is a set of glue positions that every route between a driver and an
unreachable component must cross. Compute cuts separately for every rider set.
"""

import argparse
import subprocess
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from ortools.sat.python import cp_model

from assemble import HERE

DIR = (4096, -4096, 64, -64, 1, -1)
X = DIR[0]


def point(x, y, z):
    return x * X + y * 64 + z


def read(path):
    header, *rows = path.read_text().splitlines()
    n, _ = map(int, header.split())
    body = defaultdict(set)
    for row in rows:
        i, k, x, y, z, *_ = row.split()
        body[int(i), k].add(point(int(x), int(y), int(z)))
    return n, body


def domains(path, n, limit):
    cmd = [
        HERE / "ring",
        str(n),
        str(limit),
        "-1",
        "-1",
        "O",
        "5",
        "unused",
        "1",
        "beam",
        "dump",
        path,
    ]
    dd = defaultdict(set)
    req = defaultdict(set)
    for line in subprocess.check_output(cmd, text=True).splitlines():
        i, x, y, z, required = map(int, line.split())
        p = point(x, y, z)
        dd[i].add(p)
        if required:
            req[i].add(p)
    return dd, req


def motions(i, n, body):
    prev = (i - 1) % n
    shift = 2 if prev % 3 == 2 else 0
    carried = {p + (shift - 2) * X for p in body[prev, "H"]}
    pickup = next(iter(body[prev, "S"])) + (shift - 3) * X
    static = body[i, "R"] | body[i, "S"]
    for m in range(2, 6):
        for actor in sorted(body[i, "H"]) if m < 5 else [None]:
            root = pickup if m == 5 else actor + X
            for own in combinations(body[i, "H"] - {actor}, max(0, 4 - m)):
                for spent in combinations(carried, min(3, m - 1)):
                    yield root, static | set(own) | set(spent)


def traverse(start, nodes, edges):
    reached = {start}
    stack = [start]
    while stack:
        for v in edges[stack.pop()]:
            if v in nodes and v not in reached:
                reached.add(v)
                stack.append(v)
    return reached


def minimum(i, n, body, domain, required, cap):
    model = cp_model.CpModel()
    var = {p: model.new_bool_var(str(p)) for p in domain}
    for p in required:
        model.add(var[p] == 1)
    model.add(sum(var.values()) <= cap)
    # A glue block or attached leaf can also drive a forward obstruction.
    variants = []
    for root, leaves in motions(i, n, body):
        possible = domain | leaves
        edges = {
            p: {p + d for d in (DIR if p in domain else (X,)) if p + d in possible}
            for p in possible
        }
        reverse = {p: set() for p in possible}
        for p, ns in edges.items():
            for q in ns:
                reverse[q].add(p)
        variants.append((root, leaves, edges, reverse))
        for leaf in leaves:
            if not (reverse[leaf] & leaves):
                model.add_bool_or(var[q] for q in reverse[leaf])
    for p in domain:
        model.add_hint(var[p], int(p in body[i, "G"]))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    known = set()
    for step in range(20000):
        status = solver.solve(model)
        if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
            return None, step
        active = {p for p in domain if solver.value(var[p])}
        cuts = set()
        for root, leaves, edges, reverse in variants:
            selected = active | leaves
            reached = traverse(root, selected, edges)
            if len(reached) == len(selected):
                continue
            outward = frozenset(
                q for p in reached for q in edges[p] if q not in selected
            )
            # At least one missing required terminal forces this cut globally.
            if (required | leaves) - reached:
                cuts.add((None, outward))
            for target in selected - reached:
                island = traverse(target, selected, reverse)
                boundary = frozenset(
                    q for p in island for q in reverse[p] if q not in selected
                )
                if island & (required | leaves):
                    cuts.add((None, boundary))
                else:
                    cuts.add((target, boundary))
        if not cuts:
            return active, step
        for target, boundary in cuts - known:
            clause = [var[p] for p in boundary]
            if target is not None:
                clause.append(var[target].Not())
            model.add_bool_or(clause)
        known.update(cuts)
    raise RuntimeError("iteration bound")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("geometry", type=Path)
    ap.add_argument("pl", type=int)
    args = ap.parse_args()
    n, body = read(args.geometry)
    dd, req = domains(args.geometry, n, args.pl)
    for i in range(n):
        cap = args.pl - 4 - len(body[i, "R"])
        g, steps = minimum(i, n, body, dd[i], req[i], cap)
        print(
            i,
            "cap",
            cap,
            "glue",
            len(g) if g is not None else "infeasible",
            "cut rounds",
            steps,
            flush=True,
        )
