"""Cache invalidation for bank-only GitHub Pages deployments."""

from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from fastflyer import Block, Flyer, Kind
from scripts import build_site
from scripts.update_bank import engine_fingerprint


class SiteBuildTests(unittest.TestCase):
    def test_engine_fingerprint_ignores_checkout_line_endings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "src").mkdir()
            source = root / "src/lib.rs"
            source.write_bytes(b"first\r\nsecond\r\n")
            windows = engine_fingerprint(root)
            source.write_bytes(b"first\nsecond\n")
            self.assertEqual(windows, engine_fingerprint(root))
            source.write_bytes(b"changed\n")
            self.assertNotEqual(windows, engine_fingerprint(root))

    def test_categories_are_overlapping_and_read_blocks_not_folders(self):
        flyer = Flyer()
        flyer.set((0, 0, 0), Block.piston(1, sticky=True))
        flyer.set((1, 0, 0), Block.observer(0))
        self.assertEqual(build_site.categories(flyer), ["pulling_only", "observer_only"])
        flyer.set((0, 0, 0), Block.piston(0, sticky=True))
        self.assertEqual(build_site.categories(flyer), ["pushing_only", "observer_only"])
        flyer.set((2, 0, 0), Block.rod(0))
        self.assertEqual(build_site.categories(flyer), ["pushing_only"])
        flyer.remove((1, 0, 0))
        self.assertEqual(build_site.categories(flyer), ["pushing_only", "no_observer"])
        flyer.set((3, 0, 0), Block.piston(1))
        self.assertEqual(build_site.categories(flyer), ["no_observer"])
        self.assertNotIn("pushing_only", build_site.categories(Flyer()))
        self.assertNotIn("pulling_only", build_site.categories(Flyer()))

    def test_bank_change_versions_manifest_app_and_flyer(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            viewer, dist, bank = root / "viewer", root / "dist", root / "flyers/bank"
            viewer.mkdir()
            bank.mkdir(parents=True)
            for name in ("app.js", "index.html", "style.css", "flyer-io.js"):
                shutil.copy2(build_site.VIEWER / name, viewer / name)
            shutil.copytree(build_site.VIEWER / build_site.MULTIPLAYER, viewer / build_site.MULTIPLAYER)
            modules = viewer / "node_modules"
            for source in build_site.VENDOR:
                dependency = modules / source.replace("*", "index")
                dependency.parent.mkdir(parents=True, exist_ok=True)
                dependency.write_text('import "./utils.mjs";\n//# sourceMappingURL=index.mjs.map\n', encoding="utf-8")
            wasm = root / "target/wasm32-unknown-unknown/release/fastflyer.wasm"
            wasm.parent.mkdir(parents=True)
            wasm.write_bytes(b"test wasm")
            flyer = Flyer(push_limit=22)
            flyer.set((0, 0, 0), Block(Kind.SLIME))
            path = bank / "sample.flyer"
            flyer.save(path)
            (bank / "catalogue.json").write_text(json.dumps({
                "format_version": 1, "engine_sha256": engine_fingerprint(root),
                "entries": {path.relative_to(root).as_posix(): {
                    "sha256": sha256(path.read_bytes()).hexdigest(), "ticks": 10_000,
                    "distance": 1000, "speed_bps": 1, "endpoint_conserved": True,
                }},
            }), encoding="utf-8")
            with patch.multiple(build_site, ROOT=root, VIEWER=viewer, DIST=dist, BANK=bank), patch("builtins.print"):
                build_site.main()
                old_app = (dist / "app.js").read_text(encoding="utf-8")
                old_html = (dist / "index.html").read_text(encoding="utf-8")
                old_entry = json.loads((dist / "bank.json").read_text())[0]
                flyer.set((1, 0, 0), Block(Kind.HONEY))
                flyer.save(path)
                build_site.main()
            app = (dist / "app.js").read_text(encoding="utf-8")
            entry = json.loads((dist / "bank.json").read_text())[0]
            manifest_hash = sha256((dist / "bank.json").read_bytes()).hexdigest()[:12]
            self.assertNotEqual(old_entry["version"], entry["version"])
            self.assertEqual(old_entry["speed_bps"], 1)
            self.assertIsNone(entry["speed_bps"], "Changed flyers must not retain an old speed")
            self.assertEqual(entry["version"], sha256(path.read_bytes()).hexdigest()[:12])
            self.assertIn(f"bank.json?v={manifest_hash}", app)
            self.assertNotIn("__BANK_HASH__", app)
            self.assertNotIn("__IO_HASH__", app)
            self.assertNotIn("__MP_HASH__", app)
            for module in (dist / build_site.MULTIPLAYER).glob("*.js"):
                self.assertNotIn("__MP_HASH__", module.read_text(encoding="utf-8"))
            self.assertFalse(list((dist / build_site.MULTIPLAYER).glob("*.test.js")))
            # Vendored .mjs modules are served as .js with matching relative imports.
            core = (dist / "vendor/trystero-core/index.js").read_text(encoding="utf-8")
            self.assertIn('import "./utils.js";', core)
            self.assertNotIn("sourceMappingURL", core)
            self.assertNotEqual(old_app, app)
            self.assertNotEqual(old_html, (dist / "index.html").read_text(encoding="utf-8"))
            self.assertEqual(path.read_bytes(), (dist / entry["path"]).read_bytes())


if __name__ == "__main__":
    unittest.main()
