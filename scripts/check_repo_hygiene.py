"""Reject compiled binaries, pickles, and oversized files from Git.

Usage:
    python scripts/check_repo_hygiene.py           # check every tracked file
    python scripts/check_repo_hygiene.py --staged  # check files staged for commit

Run by `.githooks/pre-commit` (enable once with
`git config core.hooksPath .githooks`) and by the GitHub Pages workflow.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 1_000_000
BLOCKED_SUFFIXES = {
    ".exe", ".pdb", ".dll", ".so", ".dylib", ".a", ".lib", ".rlib", ".o",
    ".obj", ".wasm", ".pkl", ".pyc", ".pyo", ".zip", ".7z",
}
# Mojang structure exports are binary but are hand-built source inputs.
ALLOWED_BINARY_SUFFIXES = {".mcstructure"}


def git_paths(staged: bool) -> list[str]:
    if staged:
        args = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"]
    else:
        args = ["git", "ls-files", "-z"]
    out = subprocess.run(args, cwd=ROOT, check=True, capture_output=True).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def staged_size(path: str) -> int:
    out = subprocess.run(
        ["git", "cat-file", "-s", f":{path}"], cwd=ROOT, check=True, capture_output=True
    ).stdout
    return int(out)


def problems(staged: bool) -> list[str]:
    found = []
    for path in git_paths(staged):
        suffix = Path(path).suffix.lower()
        if suffix in BLOCKED_SUFFIXES:
            found.append(f"blocked file type: {path}")
            continue
        size = staged_size(path) if staged else (ROOT / path).stat().st_size
        if size > MAX_BYTES and suffix not in ALLOWED_BINARY_SUFFIXES:
            found.append(f"larger than {MAX_BYTES // 1000} kB ({size // 1000} kB): {path}")
    return found


def main() -> int:
    found = problems("--staged" in sys.argv[1:])
    for line in found:
        print(line, file=sys.stderr)
    if found:
        print(
            "Keep generated output in an ignored out/ directory or summarise it as CSV.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
