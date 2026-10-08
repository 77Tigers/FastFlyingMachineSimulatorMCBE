import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fastflyer import research  # noqa: E402
import bank_add  # noqa: E402


def sample_rows(n=80, limit=8, distance=2500, boundaries=1250, load=8):
    return [{"rng": i, "phase_x": 0, "phase_z": 0, "limit": limit, "distance": distance,
             "max_successful_action": load, "boundaries": boundaries, "pass": True} for i in range(n)]


class ParseTests(unittest.TestCase):
    def test_measure_line(self):
        line = ("file=C:/a b/x.flyer limit=8 rng_final=123 ticks=10000 start_min_x=-3 end_min_x=2497 distance=2500 "
                "initial_kinds=[0, 1, 2] final_kinds=[0, 1, 2] first_repeat=Some((0, 8, 2)) traced=false "
                "max_successful_action=8")
        d = research.parse_kv(line)
        self.assertEqual((d["limit"], d["start_min_x"], d["distance"]), (8, -3, 2500))
        self.assertEqual(d["file"], "C:/a b/x.flyer")
        self.assertEqual(d["initial_kinds"], "[0, 1, 2]")
        self.assertEqual(d["first_repeat"], "Some((0, 8, 2))")
        self.assertIs(d["traced"], False)

    def test_verify_line_has_bare_prefix(self):
        d = research.parse_kv("verify pass=true file=f.flyer first_failure_tick=- distance=40")
        self.assertIs(d["pass"], True)
        self.assertEqual((d["first_failure_tick"], d["distance"]), ("-", 40))


class LedgerTests(unittest.TestCase):
    ROW = "8,new,0,2500,2500,168,75000"

    def append(self, initial: bytes) -> bytes:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "results.csv"
            path.write_bytes(initial)
            self.assertTrue(bank_add.append_csv_row(path, self.ROW))
            return path.read_bytes()

    def test_lf(self):
        self.assertEqual(self.append(b"h\na,b\n"), b"h\na,b\n" + self.ROW.encode() + b"\n")

    def test_crlf(self):
        self.assertEqual(self.append(b"h\r\na,b\r\n"), b"h\r\na,b\r\n" + self.ROW.encode() + b"\r\n")

    def test_no_trailing_newline_lf_and_crlf(self):
        self.assertEqual(self.append(b"h\na,b"), b"h\na,b\n" + self.ROW.encode() + b"\n")
        self.assertEqual(self.append(b"h\r\na,b"), b"h\r\na,b\r\n" + self.ROW.encode() + b"\r\n")

    def test_mixed_follows_last_line(self):
        self.assertEqual(self.append(b"h\na,b\r\n"), b"h\na,b\r\n" + self.ROW.encode() + b"\r\n")

    def test_existing_row_not_duplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "results.csv"
            data = b"h\r\n" + self.ROW.encode() + b"\r\n"
            path.write_bytes(data)
            self.assertFalse(bank_add.append_csv_row(path, self.ROW))
            self.assertEqual(path.read_bytes(), data)
            self.assertIsNone(bank_add.ledger_conflict(path, 8, "new", self.ROW))
            self.assertEqual(bank_add.ledger_conflict(path, 8, "new", "8,new,0,1,1,1,1"), self.ROW)


class SampleAcceptanceTests(unittest.TestCase):
    def test_all_pass(self):
        self.assertEqual(bank_add.check_samples(sample_rows(), 8, 2), [])

    def test_one_failure(self):
        rows = sample_rows()
        rows[17]["pass"] = False
        problems = bank_add.check_samples(rows, 8, 2)
        self.assertEqual(len(problems), 1)
        self.assertIn("1 sample(s) failed", problems[0])

    def test_wrong_limit(self):
        self.assertTrue(any("limit" in p for p in bank_add.check_samples(sample_rows(limit=9), 8)))

    def test_load_above_limit(self):
        self.assertTrue(any("max_successful_action" in p for p in bank_add.check_samples(sample_rows(load=9), 8)))

    def test_speed_mode_distances_may_differ(self):
        rows = sample_rows()
        rows[3]["distance"] = 2600
        self.assertEqual(bank_add.check_samples(rows, 8, distance=2500), [])
        self.assertTrue(bank_add.check_samples(rows, 8, 2))  # exact mode still wants one shared distance

    def test_speed_mode_short_row(self):
        rows = sample_rows()
        rows[0]["distance"] = 2499
        self.assertTrue(any("distance" in p for p in bank_add.check_samples(rows, 8, distance=2500)))

    def test_speed_mode_ignores_boundaries(self):
        self.assertEqual(bank_add.check_samples(sample_rows(boundaries=0), 8, distance=2500), [])

    def test_wrong_count_and_advance(self):
        self.assertTrue(bank_add.check_samples(sample_rows(79), 8))
        self.assertTrue(any("advance" in p for p in bank_add.check_samples(sample_rows(), 8, 3)))


class CatalogueTests(unittest.TestCase):
    def test_order_follows_bank_paths(self):
        a, b = bank_add.ROOT / "flyers/bank/pl3/a.flyer", bank_add.ROOT / "flyers/bank/pl3/b.flyer"
        cat = {"format_version": 1, "entries": {"flyers/bank/pl3/b.flyer": {"x": 1}}}
        text = bank_add.catalogue_text(cat, "flyers/bank/pl3/a.flyer", {"x": 2}, [a, b])
        self.assertLess(text.index("pl3/a.flyer"), text.index("pl3/b.flyer"))
        self.assertTrue(text.endswith("}\n"))
        with self.assertRaises(SystemExit):
            bank_add.catalogue_text(cat, "flyers/bank/pl3/a.flyer", {"x": 2}, [b])


@unittest.skipUnless(shutil.which("cargo"), "cargo not installed")
class BinaryTests(unittest.TestCase):
    def test_measure_short(self):
        flyer = next((research.BANK_DIR / "pl3").glob("*.flyer"), None)
        if flyer is None or not research.binary("fastflyer-research", build=False).exists():
            self.skipTest("no bank flyer or research binary built")
        d = research.measure(flyer, ticks=40)
        self.assertEqual(d["ticks"], 40)
        self.assertIn("distance", d)


if __name__ == "__main__":
    unittest.main()
