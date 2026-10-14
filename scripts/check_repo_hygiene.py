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


def staged_sizes() -> dict[str, int]:
    """Map each staged (added/copied/modified/renamed) path to its blob size.

    One `git diff` plus one `git cat-file --batch-check` for the whole commit,
    instead of a git process per file (slow on Windows/OneDrive).
    """
    raw = subprocess.run(
        ["git", "diff", "--cached", "--raw", "--no-abbrev", "-z", "--diff-filter=ACMR"],
        cwd=ROOT, check=True, capture_output=True,
    ).stdout.decode("utf-8")
    fields = raw.split("\0")
    entries: list[tuple[str, str]] = []  # (path, blob sha)
    i = 0
    while i + 1 < len(fields) and fields[i].startswith(":"):
        meta = fields[i].split()  # :old-mode new-mode old-sha new-sha status
        if meta[4][0] in "RC":  # rename/copy list source then destination
            path, i = fields[i + 2], i + 3
        else:
            path, i = fields[i + 1], i + 2
        entries.append((path, meta[3]))
    if not entries:
        return {}
    shas = "".join(f"{sha}\n" for _, sha in entries)
    sizes = subprocess.run(
        ["git", "cat-file", "--batch-check=%(objectsize)"],
        cwd=ROOT, check=True, capture_output=True, input=shas.encode(),
    ).stdout.decode().split()
    return {path: int(size) for (path, _), size in zip(entries, sizes)}


def tracked_sizes() -> dict[str, int]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True).stdout
    paths = [p for p in out.decode("utf-8").split("\0") if p]
    return {p: (ROOT / p).stat().st_size for p in paths}


def problems(staged: bool) -> list[str]:
    found = []
    for path, size in (staged_sizes() if staged else tracked_sizes()).items():
        suffix = Path(path).suffix.lower()
        if suffix in BLOCKED_SUFFIXES:
            found.append(f"blocked file type: {path}")
        elif size > MAX_BYTES and suffix not in ALLOWED_BINARY_SUFFIXES:
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
