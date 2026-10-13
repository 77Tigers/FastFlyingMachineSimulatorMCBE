from dataclasses import replace
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from extension_contract import ContractError, _prescribed_driver_path, load_contract, run_case


class PrescribedSchedulingRegressionTests(unittest.TestCase):
    def test_n4_14_interleaved_input_permutation_replays_load_failure(self):
        """The published n4_14 contract passes both extremes but not interleaving."""
        contract_path = ROOT / "flyers" / "extension_bank" / "n4" / "n4_14" / "before_natural.json"
        if not contract_path.is_file():
            self.skipTest("published n4_14 fixture is not present")
        try:
            driver = _prescribed_driver_path()
        except ContractError:
            self.skipTest("build target/release/extension-prescribe to run integration test")

        base = load_contract(contract_path)
        sample = (0, 0, 0)
        before = run_case(replace(base, prescribed_order="before_natural"), driver, sample)
        after = run_case(replace(base, prescribed_order="after_natural"), driver, sample)
        interleaved = run_case(replace(base, prescribed_order="interleaved"), driver, sample)
        replay = run_case(replace(base, prescribed_order="interleaved"), driver, sample)

        self.assertTrue(before["passed"], before["diagnostic"])
        self.assertTrue(after["passed"], after["diagnostic"])
        self.assertFalse(interleaved["passed"])
        failure = interleaved["first_failure"]
        self.assertEqual(failure["stage"], "prescribed")
        self.assertEqual(failure["code"], "prescribed_move_failed")
        self.assertEqual(failure["tick"], 14)
        self.assertEqual(failure["expected"], {"input": [15, 0, 3], "max_load": 16})
        self.assertEqual(failure["actual"]["failure"]["reason"], "prescribed load limit exceeded")
        self.assertEqual(len(failure["actual"]["sources"]), 17)

        replay_failure = replay["first_failure"]
        self.assertEqual(replay_failure["tick"], failure["tick"])
        self.assertEqual(replay_failure["expected"]["input"], failure["expected"]["input"])
        self.assertEqual(replay_failure["actual"]["sources"], failure["actual"]["sources"])


if __name__ == "__main__":
    unittest.main()
