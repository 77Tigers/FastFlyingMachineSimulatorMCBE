#!/usr/bin/env python3
"""Check relative markdown links in tracked .md files (std-lib only).

Excludes flyers/docs/archive/ and node_modules. Links to gitignored .flyer files that exist locally
count as resolving but are listed separately (they will not exist on a fresh clone).
Exit status 1 if any link is broken.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)|!\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^\s*(```|~~~)")
SKIP = ("flyers/docs/archive/",)


def git(*args: str) -> list[str]:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [line for line in out.split("\0") if line]


def main() -> int:
    files = [f for f in git("ls-files", "-z", "--", "*.md")
             if not f.startswith(SKIP) and "node_modules/" not in f and (ROOT / f).exists()]
    tracked = set(git("ls-files", "-z"))
    broken: list[str] = []
    ignored: list[str] = []
    for f in sorted(files):
        base = (ROOT / f).parent
        in_fence = False
        for no, line in enumerate((ROOT / f).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if FENCE.match(line):
                in_fence = not in_fence
            if in_fence:
                continue
            for m in LINK.finditer(re.sub(r"`[^`]*`", "", line)):
                target = m.group(1) or m.group(2)
                if re.match(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|#|//)", target):
                    continue
                path = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not path:
                    continue
                dest = (base / path).resolve()
                if not dest.exists():
                    broken.append(f"{f}:{no}: {target}")
                elif dest.suffix == ".flyer":
                    try:
                        rel = dest.relative_to(ROOT).as_posix()
                    except ValueError:
                        continue
                    if rel not in tracked:
                        ignored.append(f"{f}:{no}: {target}")
    if ignored:
        print(f"warning: {len(ignored)} link(s) to untracked/gitignored .flyer files (missing on a fresh clone):")
        print("\n".join("  " + s for s in ignored))
    if broken:
        print(f"{len(broken)} broken link(s):")
        print("\n".join("  " + s for s in broken))
        return 1
    print(f"ok: {len(files)} markdown files checked, no broken links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
