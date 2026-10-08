"""Thin Python wrappers around the research binaries (no third-party dependencies).

Replaces per-script boilerplate: locating ``target/release/<tool>``, building it, and
parsing the ``key=value`` / CSV output of ``fastflyer-research``.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
BANK_DIR = REPO_ROOT / "flyers" / "bank"
EXPERIMENTS_DIR = REPO_ROOT / "flyers" / "WIP" / "experiments"

_ROOT_TOOLS = {"fastflyer-sim", "fastflyer-bank-stats", "fastflyer-viewer"}
_TOOLS_BIN_DIR = REPO_ROOT / "tools" / "src" / "bin"
_built: set[str] = set()
_KEY = re.compile(r"(?:^|\s)([A-Za-z_][A-Za-z0-9_]*)=")


def binary(name: str, build: bool = True) -> Path:
    """Path of ``target/release/<name>[.exe]``; with ``build``, run ``cargo build`` once per process."""
    if name in _ROOT_TOOLS:
        cmd = ["cargo", "build", "--release", "--bin", name]
    elif (_TOOLS_BIN_DIR / f"{name}.rs").is_file():
        cmd = ["cargo", "build", "--release", "--manifest-path", "tools/Cargo.toml", "--target-dir", "target"]
    else:
        raise ValueError(f"unknown tool {name!r}")
    if build and name not in _built:
        subprocess.run(cmd, cwd=REPO_ROOT, check=True)
        _built.add(name)
    return REPO_ROOT / "target" / "release" / (name + (".exe" if os.name == "nt" else ""))


def _tool(name: str) -> Path:
    path = binary(name, build=False)
    return path if path.exists() else binary(name)


def _run(name: str, args: Iterable[object]) -> subprocess.CompletedProcess:
    cmd = [str(_tool(name)), *map(str, args)]
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)


def _tool_error(proc: subprocess.CompletedProcess, what: str) -> RuntimeError:
    return RuntimeError(f"{what} failed (exit {proc.returncode}): {(proc.stderr or proc.stdout).strip()}")


def _value(text: str) -> Any:
    text = text.strip()
    if text in ("true", "false"):
        return text == "true"
    try:
        return int(text)
    except ValueError:
        return text


def parse_kv(line: str) -> dict[str, Any]:
    """Parse ``key=value key=value ...`` (values may contain spaces); numbers become ints, true/false bools."""
    marks = list(_KEY.finditer(line))
    return {
        m.group(1): _value(line[m.end() : marks[i + 1].start() if i + 1 < len(marks) else len(line)])
        for i, m in enumerate(marks)
    }


def _first_line(stdout: str, prefix: str = "") -> str:
    for line in stdout.splitlines():
        if line.startswith(prefix) and "=" in line:
            return line
    return ""


def simulate(src: str | Path, dst: str | Path, ticks: int) -> None:
    """Run ``fastflyer-sim SRC DST TICKS``; raises ``subprocess.CalledProcessError`` on failure."""
    subprocess.run([str(_tool("fastflyer-sim")), str(src), str(dst), str(ticks)],
                   check=True, capture_output=True, cwd=REPO_ROOT)


def measure(path: str | Path, ticks: int = 10000, period: int = 0, audit: bool = False) -> dict[str, Any]:
    """Run ``fastflyer-research measure|audit`` and return its parsed key=value fields."""
    proc = _run("fastflyer-research", ["audit" if audit else "measure", Path(path).resolve(), ticks, period])
    line = _first_line(proc.stdout, "file=")
    if proc.returncode or not line:
        raise _tool_error(proc, "measure")
    return parse_kv(line)


def verify(path: str | Path, period: int, advance: int, ticks: int = 10000) -> dict[str, Any]:
    """Run ``verify``; returns the summary dict (``pass`` False on a failed check). Raises only on tool errors."""
    proc = _run("fastflyer-research", ["verify", Path(path).resolve(), ticks, "--period", period, "--advance", advance])
    line = _first_line(proc.stdout, "verify ")
    if not line:
        raise _tool_error(proc, "verify")
    return parse_kv(line)


def _read_rows(path: Path) -> list[dict[str, Any]]:
    with open(path, newline="", encoding="utf-8") as f:
        return [{k: _value(v) for k, v in row.items()} for row in csv.DictReader(f)]


def samples(path: str | Path, period: int | None, advance: int | None, out: str | Path, ticks: int = 10000,
            jobs: int | None = None, distance: int | None = None, exact: bool = False) -> list[dict[str, Any]]:
    """Run the 80-case ``samples`` audit, write CSV to ``out`` and return its rows (failures included).

    ``distance``: pass = clean and distance >= that (the bank standard). ``period``/``advance`` add the exact columns;
    with ``exact=True`` (or without ``distance``) pass = exact recurrence."""
    args: list[object] = ["samples", Path(path).resolve(), "--out", Path(out).resolve(), "--ticks", ticks]
    if distance is not None:
        args += ["--distance", distance]
    if period is not None:
        args += ["--period", period]
    if advance is not None:
        args += ["--advance", advance]
    if exact:
        args.append("--exact")
    if jobs:
        args += ["--jobs", jobs]
    proc = _run("fastflyer-research", args)
    if "samples passed=" not in proc.stdout:  # exit 1 with this line only means "not all 80 passed"
        raise _tool_error(proc, "samples")
    return _read_rows(Path(out))


def screen(directory: str | Path, ticks: int = 160, out: str | Path | None = None,
           jobs: int | None = None) -> list[dict[str, Any]]:
    """Screen every flyer in ``directory`` and return the per-flyer CSV rows (temp CSV if ``out`` is None)."""
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = Path(out).resolve() if out else Path(tmp) / "screen.csv"
        args: list[object] = ["screen", Path(directory).resolve(), ticks, "--out", csv_path]
        if jobs:
            args += ["--jobs", jobs]
        proc = _run("fastflyer-research", args)
        if proc.returncode or not csv_path.exists():
            raise _tool_error(proc, "screen")
        return _read_rows(csv_path)


def bank_stats(paths: Iterable[str | Path], ticks: int = 10000) -> list[dict[str, Any]]:
    """Run ``fastflyer-bank-stats``; one dict per path, in input order (catalogue.json field names)."""
    resolved = [Path(p).resolve() for p in paths]
    if not resolved:
        return []
    proc = _run("fastflyer-bank-stats", [ticks, *resolved])
    if proc.returncode:
        raise _tool_error(proc, "bank-stats")
    out: list[dict[str, Any]] = [{}] * len(resolved)
    for line in proc.stdout.splitlines():
        index, distance, extensions, failures, conserved = line.split("\t")
        out[int(index)] = {"path": resolved[int(index)], "distance": int(distance), "extensions": int(extensions),
                           "extension_failures": int(failures), "endpoint_conserved": conserved == "true"}
    return out
