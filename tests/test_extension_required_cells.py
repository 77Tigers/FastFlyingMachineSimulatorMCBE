import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from extension_contract import CaseChecker, Contract, ContractError, load_contract, run_case, _driver_path


class RequiredCellsTests(unittest.TestCase):
    def test_missing_or_changed_untagged_cell_rejected(self):
        spec = Contract("required", Path("unused"), 2, 0, 1, (),
                        required_cells=(((0, 0, 0), 3),))
        for cells in ([], [[0, 0, 0, 4]]):
            with self.subTest(cells=cells), self.assertRaises(ContractError) as caught:
                CaseChecker(spec, {"initial": cells, "initial_owners": []})
            self.assertEqual(caught.exception.first_failure["code"], "required_cell_mismatch")

    def test_required_cell_allows_additional_hardware(self):
        spec = Contract("required", Path("unused"), 2, 0, 1, (),
                        required_cells=(((0, 0, 0), 3),))
        CaseChecker(spec, {"initial": [[0, 0, 0, 3], [2, 0, 0, 4]], "initial_owners": []})

    def test_schema_rejects_duplicate_and_boolean_cells(self):
        raw = {"version": 1, "name": "required", "flyer": "unused.flyer",
               "period_ticks": 2, "advance": 0,
               "ports": [{"name": "out", "role": "output", "at": [0, 0, 0], "word": "w"}]}
        with tempfile.TemporaryDirectory(dir=ROOT / "target") as temp:
            path = Path(temp) / "contract.json"
            for cells in ([{"at": [0, 0, 0], "cell": True}],
                          [{"at": [0, 0, 0], "cell": 3}] * 2):
                raw["required_cells"] = cells
                path.write_text(json.dumps(raw), encoding="utf-8")
                with self.assertRaises(ContractError):
                    load_contract(path)

    def test_run_case_preserves_initial_failure(self):
        from fastflyer import Block, Flyer, Kind
        try:
            driver = _driver_path()
        except ContractError:
            self.skipTest("build target/release/extension-trace to run integration test")
        with tempfile.TemporaryDirectory(dir=ROOT / "target") as temp:
            path = Path(temp) / "fixture.flyer"
            flyer = Flyer()
            flyer.set((0, 0, 0), Block(Kind.SMOOTH_STONE))
            flyer.save(path)
            spec = Contract("required", path, 2, 0, 1, (),
                            required_cells=(((1, 0, 0), 3),))
            result = run_case(spec, driver, None)
        self.assertFalse(result["passed"])
        self.assertEqual(result["first_failure"]["code"], "required_cell_mismatch")


if __name__ == "__main__":
    unittest.main()
