"""Reject generated build output, personal paths, obvious secrets and oversized files.

Usage:
    python scripts/check_repo_hygiene.py           # check every tracked file
    python scripts/check_repo_hygiene.py --staged  # check files staged for commit

Run by `.githooks/pre-commit` (enable once with
`git config core.hooksPath .githooks`) and by the GitHub Pages workflow.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 1_000_000
BLOCKED_SUFFIXES = {
    ".exe", ".pdb", ".dll", ".so", ".dylib", ".a", ".lib", ".rlib", ".o",
    ".obj", ".wasm", ".pkl", ".pyc", ".pyo", ".zip", ".7z", ".rmeta", ".exp",
}
# Mojang structure exports are binary but are hand-built source inputs.
ALLOWED_BINARY_SUFFIXES = {".mcstructure"}
# These match actual home directories, including JSON-escaped Windows paths.
# The expression itself and relative paths such as docs/home/example are harmless.
PERSONAL_PATH = re.compile(
    r"(?<![\w/])(?:[A-Za-z]:[\\/]+Users[\\/]+|/c/Users/|/(?:home|Users)/)[\w.-][^\\/\s\"'`<>]*",
    re.IGNORECASE,
)
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    "API token": re.compile(r"\b(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}|xox[baprs]-[A-Za-z0-9-]{20,}|AIza[0-9A-Za-z_-]{35})\b"),
    "credential URL": re.compile(r"\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/:@]+:[^\s/@]+@"),
}


def staged_blobs(paths: list[str]) -> dict[str, bytes]:
    """Read the index, not possibly different working files, in one Git process."""
    if not paths:
        return {}
    # Newline names cannot be addressed safely by the line-based batch protocol.
    safe = [p for p in paths if "\n" not in p and "\r" not in p]
    raw = subprocess.run(
        ["git", "cat-file", "--batch"], cwd=ROOT, check=True, capture_output=True,
        input="".join(f":{p}\n" for p in safe).encode("utf-8"),
    ).stdout
    result = {}
    offset = 0
    for path in safe:
        end = raw.index(b"\n", offset)
        size = int(raw[offset:end].split()[-1])
        result[path] = raw[end + 1:end + 1 + size]
        offset = end + size + 2
    return result


def content_problems(path: str, data: bytes) -> list[str]:
    """Return locations/categories only; never echo potential secret values."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return []
    found = []
    for category, pattern in (("personal home-directory path", PERSONAL_PATH), *SECRET_PATTERNS.items()):
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            found.append(f"{category}: {path}:{line}")
    return found


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
    # A tracked deletion may already be pending in the working tree.
    return {p: (ROOT / p).stat().st_size for p in paths if (ROOT / p).is_file()}


def problems(staged: bool) -> list[str]:
    found = []
    sizes = staged_sizes() if staged else tracked_sizes()
    blobs = staged_blobs(list(sizes)) if staged else {}
    for path, size in sizes.items():
        suffix = Path(path).suffix.lower()
        parts = Path(path).parts
        name = Path(path).name.lower()
        if "\n" in path or "\r" in path:
            found.append(f"newline in filename: {path!r}")
            continue
        if any(p == "target" or p.startswith("target-") or p in {"node_modules", "__pycache__", ".venv"} for p in parts):
            found.append(f"generated build/cache directory: {path}")
        elif name in {".env", "id_rsa", "id_ed25519", "credentials", "credentials.json"} or (name.startswith(".env.") and name not in {".env.example", ".env.sample", ".env.template"}):
            found.append(f"local credential/config file: {path}")
        elif suffix in BLOCKED_SUFFIXES:
            found.append(f"blocked file type: {path}")
        elif size > MAX_BYTES and suffix not in ALLOWED_BINARY_SUFFIXES:
            found.append(f"larger than {MAX_BYTES // 1000} kB ({size // 1000} kB): {path}")
        found.extend(content_problems(path, blobs[path] if staged else (ROOT / path).read_bytes()))
    return found


def main() -> int:
    found = problems("--staged" in sys.argv[1:])
    for line in found:
        print(line, file=sys.stderr)
    if found:
        print(
            "Keep generated output in an ignored out/ directory; use relative paths and remove credentials.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
