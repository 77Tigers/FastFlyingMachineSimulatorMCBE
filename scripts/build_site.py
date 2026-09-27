"""Assemble the serverless GitHub Pages site after Cargo and npm builds."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fastflyer import Block, Flyer, Kind

VIEWER = ROOT / "viewer"
DIST = ROOT / "dist"
BANK = ROOT / "flyers" / "bank"

def copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main() -> None:
    wasm = ROOT / "target" / "wasm32-unknown-unknown" / "release" / "fastflyer.wasm"
    if not wasm.is_file():
        raise SystemExit("Build Rust first: cargo build --release --target wasm32-unknown-unknown --lib")
    DIST.mkdir(exist_ok=True)
    for filename in ("index.html", "style.css", "app.js"):
        copy(VIEWER / filename, DIST / filename)
    copy(wasm, DIST / "fastflyer.wasm")
    digest = lambda path: sha256(path.read_bytes()).hexdigest()[:12]
    three = VIEWER / "node_modules" / "three"
    copy(three / "build" / "three.module.js", DIST / "vendor" / "three.module.js")
    copy(three / "build" / "three.core.js", DIST / "vendor" / "three.core.js")

    demo = Flyer(rng_state=2)
    demo.set((0, 0, 0), Block.piston(0))
    demo.set((1, 0, 1), Block.piston(1, sticky=True))
    demo.set((0, 0, 1), Block(Kind.SLIME))
    demo.set((1, 0, 0), Block(Kind.SLIME))
    demo.set((0, 1, 1), Block.observer(3, powered=True))
    demo.set((1, 1, 0), Block.observer(3))
    (DIST / "demo.flyer").write_bytes(demo.to_bytes())

    manifest = []
    for path in sorted(BANK.rglob("*.flyer")):
        relative = path.relative_to(ROOT)
        flyer = Flyer.load(path)
        manifest.append({
            "path": relative.as_posix(),
            "name": path.stem.replace("_", " "),
            "push_limit": flyer.push_limit,
            "blocks": flyer.occupied_count(),
            "version": digest(path),
        })
        copy(path, DIST / relative)
    (DIST / "bank.json").write_text(json.dumps(manifest, separators=(",", ":")), encoding="utf-8")
    # Include the bank contents in the app URL too: a bank-only deployment must
    # invalidate both the manifest and any previously cached flyer downloads.
    app = DIST / "app.js"
    app.write_text(app.read_text(encoding="utf-8")
        .replace("__WASM_HASH__", digest(wasm))
        .replace("__BANK_HASH__", digest(DIST / "bank.json")), encoding="utf-8")
    html = DIST / "index.html"
    html.write_text(html.read_text(encoding="utf-8")
        .replace("__STYLE_HASH__", digest(DIST / "style.css"))
        .replace("__APP_HASH__", digest(app)), encoding="utf-8")
    print(f"Built {DIST} with {len(manifest)} bank flyers")


if __name__ == "__main__":
    main()
