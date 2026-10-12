import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from extension_explain import (_geometric_reach, _hard_powered, _power_facts, _trace_executable)

EXP = ROOT / "flyers" / "WIP" / "experiments" / "extension_contract_20261011"
CANDIDATE = EXP / "blind_repair" / "out" / "candidate.flyer"
REFERENCE = EXP / "out" / "reference.flyer"
CONTRACT = EXP / "benchmarks" / "missing_source.json"
REFERENCE_CONTRACT = EXP / "benchmarks" / "reference.json"


class ExtensionExplainRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            _trace_executable()
        except FileNotFoundError as exc:
            raise unittest.SkipTest(str(exc))

    def report(self, flyer, contract, *overrides):
        command = [sys.executable, "-B", str(ROOT / "tools" / "extension_explain.py"),
                   str(flyer), "--contract", str(contract), "--tick", "2"]
        command.extend(overrides)
        output = subprocess.check_output(command, cwd=ROOT, text=True)
        return json.loads(output)

    def test_candidate_reset_is_distinct_from_unpowered_next_actors(self):
        result = self.report(CANDIDATE, CONTRACT)
        self.assertEqual(result["port"]["at_tick_start"], [14, 4, 7])
        self.assertEqual(result["port"]["expected"], "move +X")
        self.assertEqual(result["port"]["observed"], "did not move")
        actions = result["actual_piston_actions_near_port"]
        prior = next(a for a in actions if a["at"] == [12, 4, 7])
        self.assertEqual((prior["action"], prior["state_at_action"]), ("retract", 2))
        self.assertFalse(prior["powered_at_pre_power"])
        candidates = {tuple(p["at"]): p for p in result["candidate_pushers"]}
        self.assertFalse(candidates[(13, 4, 8)]["powered_at_pre_power"])
        self.assertFalse(candidates[(13, 5, 9)]["powered_at_pre_power"])
        redstone = next(s for s in result["relevant_power_sources"] if s["at"] == [13, 5, 7])
        self.assertEqual(redstone["origin"], [12, 5, 7])
        self.assertEqual(redstone["moves"][0]["to"], [13, 5, 7])
        self.assertIn("not proof", result["mechanics_note"])
        self.assertIn("sticky pull reach is not enumerated", result["candidate_scope"])

    def test_explicit_port_mode_needs_no_contract(self):
        command = [sys.executable, "-B", str(ROOT / "tools" / "extension_explain.py"),
                   str(CANDIDATE), "--port", "13", "4", "7", "--tick", "2"]
        result = json.loads(subprocess.check_output(command, cwd=ROOT, text=True))
        self.assertEqual(result["port"]["origin"], [13, 4, 7])
        self.assertEqual(result["port"]["at_tick_start"], [14, 4, 7])

    def test_reference_next_actor_moves_tag_while_previous_actor_retracts(self):
        result = self.report(REFERENCE, REFERENCE_CONTRACT,
                             "--rng", "0", "--phase-x", "0", "--phase-z", "0")
        self.assertEqual(result["port"]["movement"]["actor"], [13, 5, 9])
        actions = {tuple(a["at"]): a for a in result["actual_piston_actions_near_port"]}
        self.assertEqual(actions[(13, 5, 9)]["action"], "extend")
        self.assertTrue(actions[(13, 5, 9)]["moved_tagged_port"])
        self.assertEqual(actions[(12, 4, 8)]["action"], "retract")
        redstone = next(s for s in result["relevant_power_sources"] if s["at"] == [13, 5, 8])
        self.assertEqual(redstone["origin"], [12, 5, 8])
        self.assertEqual(result["port"]["observed"], "moved")




class ExtensionExplainMechanicsTests(unittest.TestCase):
    def test_moving_solid_does_not_receive_hard_power(self):
        rod = 8  # stationary +X rod
        moving_slime = 1 | 16
        cells = {(0, 0, 0): rod, (1, 0, 0): moving_slime}
        self.assertNotIn((1, 0, 0), _hard_powered(cells))

    def test_moving_piston_reports_adjacent_source_without_power_eligibility(self):
        moving_piston = 9 | 16  # +X, moving
        cells = {(0, 0, 0): moving_piston, (0, 1, 0): 6}
        facts = _power_facts((0, 0, 0), moving_piston, cells, set())
        self.assertEqual(facts["adjacent_power_sources"][0]["at"], [0, 1, 0])
        self.assertTrue(facts["adjacent_power_sources"][0]["eligible_soft"])
        self.assertFalse(facts["power_eligible"])
        self.assertFalse(facts["powered_at_pre_power"])

    def test_glue_reach_includes_glass_tagged_passenger(self):
        piston = 9  # state-0 +X piston
        slime = 1
        glass = 4
        cells = {(0, 0, 0): piston, (1, 0, 0): slime, (1, 1, 0): glass}
        reach = _geometric_reach((0, 0, 0), piston, (1, 1, 0), cells)
        self.assertIsNotNone(reach)
        self.assertEqual(reach["visited_closure_blocks"], 2)
        self.assertFalse(reach["legal_extension_proof"])


if __name__ == "__main__":
    unittest.main()
