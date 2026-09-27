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


class SiteBuildTests(unittest.TestCase):
    def test_bank_change_versions_manifest_app_and_flyer(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            viewer, dist, bank = root / "viewer", root / "dist", root / "flyers/bank"
            viewer.mkdir()
            bank.mkdir(parents=True)
            for name in ("app.js", "index.html", "style.css"):
                shutil.copy2(build_site.VIEWER / name, viewer / name)
            three = viewer / "node_modules/three/build"
            three.mkdir(parents=True)
            for name in ("three.module.js", "three.core.js"):
                (three / name).write_text("// test dependency", encoding="utf-8")
            wasm = root / "target/wasm32-unknown-unknown/release/fastflyer.wasm"
            wasm.parent.mkdir(parents=True)
            wasm.write_bytes(b"test wasm")
            flyer = Flyer(push_limit=22)
            flyer.set((0, 0, 0), Block(Kind.SLIME))
            path = bank / "sample.flyer"
            flyer.save(path)
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
            self.assertEqual(entry["version"], sha256(path.read_bytes()).hexdigest()[:12])
            self.assertIn(f"bank.json?v={manifest_hash}", app)
            self.assertNotIn("__BANK_HASH__", app)
            self.assertNotEqual(old_app, app)
            self.assertNotEqual(old_html, (dist / "index.html").read_text(encoding="utf-8"))
            self.assertEqual(path.read_bytes(), (dist / entry["path"]).read_bytes())


if __name__ == "__main__":
    unittest.main()
