"""Assemble the serverless GitHub Pages site after Cargo and npm builds."""

from __future__ import annotations

import json
import re
from hashlib import sha256
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fastflyer import Block, Flyer, Kind
from scripts.update_bank import engine_fingerprint

VIEWER = ROOT / "viewer"
MULTIPLAYER = "multiplayer"
# Browser copies of npm packages, as {node_modules source: dist/vendor destination}.
VENDOR = {
    "three/build/three.module.js": "three.module.js",
    "three/build/three.core.js": "three.core.js",
    "@trystero-p2p/nostr/dist/index.mjs": "trystero-nostr/index.js",
    "@trystero-p2p/core/dist/*.mjs": "trystero-core/",
    "@noble/secp256k1/index.js": "noble-secp256k1/index.js",
}
DIST = ROOT / "dist"
BANK = ROOT / "flyers" / "bank"

def categories(flyer: Flyer) -> list[str]:
    blocks = [block for _, block in flyer.blocks()]
    pistons = [block for block in blocks if block.kind == Kind.PISTON]
    tags = []
    if pistons and all(block.direction == 0 for block in pistons):
        tags.append("pushing_only")
    if pistons and all(block.sticky and block.direction == 1 for block in pistons):
        tags.append("pulling_only")
    if not any(block.kind in (Kind.REDSTONE_BLOCK, Kind.ROD) for block in blocks):
        tags.append("observer_only")
    if not any(block.kind == Kind.OBSERVER for block in blocks):
        tags.append("no_observer")
    return tags

def copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_module(source: Path, destination: Path) -> None:
    """Vendor an ES module as .js: some static servers send .mjs as text/plain,
    which browsers refuse to run. Relative .mjs imports are renamed to match."""
    if source.suffix != ".mjs":
        copy(source, destination)
        return
    text = source.read_text(encoding="utf-8")
    text = re.sub(r"""(["'])(\.{1,2}/[^"']+)\.mjs\1""", r"\1\2.js\1", text)
    text = re.sub(r"^//# sourceMappingURL=.*$", "", text, flags=re.M)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.with_suffix(".js").write_text(text, encoding="utf-8")


def main() -> None:
    wasm = ROOT / "target" / "wasm32-unknown-unknown" / "release" / "fastflyer.wasm"
    if not wasm.is_file():
        raise SystemExit("Build Rust first: cargo build --release --target wasm32-unknown-unknown --lib")
    DIST.mkdir(exist_ok=True)
    for filename in ("index.html", "style.css", "app.js", "flyer-io.js"):
        copy(VIEWER / filename, DIST / filename)
    copy(wasm, DIST / "fastflyer.wasm")
    digest = lambda path: sha256(path.read_bytes()).hexdigest()[:12]
    modules = VIEWER / "node_modules"
    for source, destination in VENDOR.items():
        if destination.endswith("/"):
            matches = sorted(modules.glob(source))
            if not matches:
                raise SystemExit(f"Missing browser dependency {source}: run npm ci --prefix viewer")
            for match in matches:
                copy_module(match, DIST / "vendor" / destination / match.name)
        else:
            copy_module(modules / source, DIST / "vendor" / destination)
    # Multiplayer modules import each other with ?v=__MP_HASH__, so one hash of
    # the whole folder busts every cached module together.
    multiplayer_sources = sorted(path for path in (VIEWER / MULTIPLAYER).glob("*.js")
                                 if not path.name.endswith(".test.js"))
    multiplayer_hash = sha256(b"".join(path.read_bytes() for path in multiplayer_sources)).hexdigest()[:12]
    shutil.rmtree(DIST / MULTIPLAYER, ignore_errors=True)
    for path in multiplayer_sources:
        target = DIST / MULTIPLAYER / path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(path.read_text(encoding="utf-8").replace("__MP_HASH__", multiplayer_hash), encoding="utf-8")

    demo = Flyer(rng_state=2)
    demo.set((0, 0, 0), Block.piston(0))
    demo.set((1, 0, 1), Block.piston(1, sticky=True))
    demo.set((0, 0, 1), Block(Kind.SLIME))
    demo.set((1, 0, 0), Block(Kind.SLIME))
    demo.set((0, 1, 1), Block.observer(3, powered=True))
    demo.set((1, 1, 0), Block.observer(3))
    (DIST / "demo.flyer").write_bytes(demo.to_bytes())

    catalogue_path = BANK / "catalogue.json"
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8")) if catalogue_path.exists() else {}
    if catalogue.get("entries") and catalogue.get("engine_sha256") != engine_fingerprint(ROOT):
        raise SystemExit("Bank measurements are stale for this simulator. Run python scripts/update_bank.py, then rebuild the site.")
    measurements = catalogue.get("entries", {}) if (catalogue.get("format_version") == 1
        and catalogue.get("engine_sha256") == engine_fingerprint(ROOT)) else {}
    manifest = []
    for path in sorted(BANK.rglob("*.flyer")):
        relative = path.relative_to(ROOT)
        flyer = Flyer.load(path)
        measurement = measurements.get(relative.as_posix())
        if measurement and (measurement.get("sha256") != sha256(path.read_bytes()).hexdigest()
                            or measurement.get("ticks") != 10_000
                            or not measurement.get("endpoint_conserved")):
            measurement = None
        manifest.append({
            "path": relative.as_posix(),
            "name": path.stem.replace("_", " "),
            "push_limit": flyer.push_limit,
            "blocks": flyer.occupied_count(),
            "version": digest(path),
            "categories": categories(flyer),
            "speed_bps": measurement["speed_bps"] if measurement else None,
            "distance": measurement["distance"] if measurement else None,
            "ticks": measurement["ticks"] if measurement else None,
        })
        copy(path, DIST / relative)
    (DIST / "bank.json").write_text(json.dumps(manifest, separators=(",", ":")), encoding="utf-8")
    # Include the bank contents in the app URL too: a bank-only deployment must
    # invalidate both the manifest and any previously cached flyer downloads.
    app = DIST / "app.js"
    app.write_text(app.read_text(encoding="utf-8")
        .replace("__WASM_HASH__", digest(wasm))
        .replace("__BANK_HASH__", digest(DIST / "bank.json"))
        .replace("__IO_HASH__", digest(DIST / "flyer-io.js"))
        .replace("__MP_HASH__", multiplayer_hash), encoding="utf-8")
    html = DIST / "index.html"
    html.write_text(html.read_text(encoding="utf-8")
        .replace("__STYLE_HASH__", digest(DIST / "style.css"))
        .replace("__APP_HASH__", digest(app)), encoding="utf-8")
    print(f"Built {DIST} with {len(manifest)} bank flyers")


if __name__ == "__main__":
    main()
