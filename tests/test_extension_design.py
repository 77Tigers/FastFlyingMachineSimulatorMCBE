import json
import contextlib
import io
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from fixture_support import fixture_root

PROJECT = Path(__file__).resolve().parents[1]
ROOT = fixture_root() / "prescribed_fixture/rear_cap"
sys.path.insert(0, str(PROJECT / "tools"))
from extension_design import DesignError, compile_design, main


class ExtensionDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads((ROOT / "rear_cap_design.json").read_text(encoding="utf-8"))

    def test_rear_cap_compiles_consistent_contract_plan_and_ordered_schedule(self):
        result = compile_design(self.raw)
        self.assertEqual(result["plan"]["period_slots"], 4)
        self.assertEqual(result["plan"]["advance"], 2)
        self.assertEqual(result["contract"]["ports"][0]["word"], "mmww")
        self.assertEqual(result["contract"]["recurrence"], "exact")
        self.assertEqual(len(result["contract"]["required_cells"]), 15)
        self.assertEqual(result["contract"]["ports"][1]["baseline_load"], [None, None, 6, 6])
        self.assertEqual(result["contract"]["ports"][0]["spare_load"], [0, 0, None, None])
        self.assertEqual(result["runtime"]["provenance"]["k1_input"][2], "internal")
        self.assertEqual(result["runtime"]["provenance"]["k1_input"][3], "supplied")
        self.assertEqual(result["prescribed_rows"], [
            {"tick": 0, "input": [3, 2, 16], "max_load": 1, "port": "redstone_input"},
            {"tick": 2, "input": [4, 2, 16], "max_load": 1, "port": "redstone_input"},
            {"tick": 6, "input": [4, 1, 17], "max_load": 6, "port": "k1_input"},
            {"tick": 8, "input": [5, 2, 16], "max_load": 1, "port": "redstone_input"},
            {"tick": 10, "input": [6, 2, 16], "max_load": 1, "port": "redstone_input"},
            {"tick": 14, "input": [6, 1, 17], "max_load": 6, "port": "k1_input"},
            {"tick": 16, "input": [7, 2, 16], "max_load": 1, "port": "redstone_input"},
            {"tick": 18, "input": [8, 2, 16], "max_load": 1, "port": "redstone_input"},
            {"tick": 22, "input": [8, 1, 17], "max_load": 6, "port": "k1_input"},
        ])
        self.assertIn('6 4 1 17 6\n8 5 2 16 1', result["prescribed_text"])

    def test_shared_offset_contact_is_preserved_in_plan(self):
        result = compile_design(self.raw)
        contact = result["plan"]["contacts"][0]
        self.assertEqual(contact["relation"], "offset")
        self.assertEqual(contact["offset"], [3, 1, 1])
        self.assertEqual(contact["slots"], [0, 1, 2, 3])

    def test_supplied_order_must_match_provenance_and_remain_ordered(self):
        bad = json.loads(json.dumps(self.raw))
        bad["supplied_order"][0] = []
        with self.assertRaisesRegex(DesignError, r"supplied_order\[0\]"):
            compile_design(bad)
        same_slot = json.loads(json.dumps(self.raw))
        same_slot["supplied_order"][0] = ["k1_input", "redstone_input"]
        with self.assertRaisesRegex(DesignError, r"supplied_order\[0\]"):
            compile_design(same_slot)

    def test_order_is_preserved_when_multiple_explicit_inputs_share_a_slot(self):
        two = json.loads(json.dumps(self.raw))
        extra = json.loads(json.dumps(two["ports"][0]))
        extra.update({"name": "second_feed", "at": [10, 2, 16]})
        two["ports"].insert(1, extra)
        two["supplied_order"][0] = ["second_feed", "redstone_input"]
        two["supplied_order"][1] = ["second_feed", "redstone_input"]
        result = compile_design(two)
        self.assertEqual([r["port"] for r in result["prescribed_rows"][:2]],
                         ["second_feed", "redstone_input"])

    def test_interleaved_order_compiles_and_cli_accepts_it(self):
        raw = json.loads(json.dumps(self.raw))
        raw["prescribed_order"] = "interleaved"
        result = compile_design(raw)
        self.assertEqual(result["contract"]["prescribed_order"], "interleaved")
        self.assertEqual(result["prescribed_rows"][0]["port"], "redstone_input")

    def test_schema_drift_and_contact_duplicates_are_rejected(self):
        drift = json.loads(json.dumps(self.raw))
        drift["new_typo_field"] = True
        with self.assertRaisesRegex(DesignError, "unknown"):
            compile_design(drift)
        drift = json.loads(json.dumps(self.raw))
        drift["contacts"][0]["surprise"] = 1
        with self.assertRaisesRegex(DesignError, "malformed contact"):
            compile_design(drift)
        drift = json.loads(json.dumps(self.raw))
        drift["contacts"][0]["slots"] = [0, 0]
        with self.assertRaisesRegex(DesignError, "duplicates"):
            compile_design(drift)

    def test_wait_provenance_must_be_null_and_move_provenance_declared(self):
        bad = json.loads(json.dumps(self.raw))
        bad["ports"][0]["provenance"][2] = "internal"
        with self.assertRaisesRegex(DesignError, "waits must be null"):
            compile_design(bad)
        bad = json.loads(json.dumps(self.raw))
        bad["ports"][1]["provenance"][2] = None
        with self.assertRaisesRegex(DesignError, "moving slots need"):
            compile_design(bad)




    def _runtime_case(self, expected_contact_offset=(0, 0, 1), feed_source="supplied", passenger_source="supplied", required_cell=1):
        sys.path.insert(0, str(Path.cwd() / "tools"))
        from extension_contract import Contract, Port, PrescribedEvent
        from extension_design import make_checker_factory
        contract = Contract(
            "runtime", Path("fixture.flyer"), 4, 1, 1,
            (Port("feed", "output", (0, 0, 0), "mw", None, None),
             Port("passenger", "output", (0, 0, 1), "mw", None, None)),
            prescribed_script=Path("script.txt"), prescribed_order="before_natural",
            prescribed=(PrescribedEvent(0, (0, 0, 0), 2),))
        initial = {"initial": [[0, 0, 0, 1], [0, 0, 1, 1]], "initial_owners": [], "steps": []}
        runtime = {"provenance": {"feed": [feed_source, None],
                                  "passenger": [passenger_source, None]},
                   "contacts": [{"name": "touch", "a": "feed", "b": "passenger",
                                 "slots": [0], "relation": "offset",
                                 "offset": list(expected_contact_offset), "required": True}],
                   "required_cells": [{"at": [0, 0, 0], "cell": required_cell}]}
        checker = make_checker_factory(runtime)(contract, initial)
        trace = {"initial": initial["initial"], "initial_owners": [], "steps": [
            {"tick": 0, "stage": "prescribed", "action": "prescribed move",
             "active_input": [0, 0, 0], "prescribed_move_id": 0,
             "prescribed_order": "before_natural",
             "movement": {"sources": [[0, 0, 0], [0, 0, 1]],
                          "destinations": [[1, 0, 0], [1, 0, 1]], "failure": None},
             "changes": [[0, 0, 0, None], [0, 0, 1, None],
                         [1, 0, 0, 17], [1, 0, 1, 17]], "owners": []},
            {"tick": 0, "stage": "chunk", "action": None, "changes": [], "owners": []}]}
        return checker, trace

    def test_runtime_accepts_supplied_passenger_provenance_and_contact(self):
        checker, trace = self._runtime_case()
        self.assertIsNone(checker.consume(trace, 0, defer_recurrence=True))
        self.assertIsNone(checker.first_failure)

    def test_runtime_rejects_supplied_passenger_mislabeled_internal(self):
        checker, trace = self._runtime_case(passenger_source="internal")
        failure = checker.consume(trace, 0, defer_recurrence=True)
        self.assertIn("expected provenance internal, observed supplied", failure)
        self.assertEqual(checker.first_failure["stage"], "provenance")
        self.assertEqual(checker.first_failure["port"], "passenger")

    def test_runtime_contact_uses_pre_action_identity_positions(self):
        checker, trace = self._runtime_case(expected_contact_offset=(1, 0, 1))
        failure = checker.consume(trace, 0, defer_recurrence=True)
        self.assertIn("contact touch", failure)
        self.assertEqual(checker.first_failure["stage"], "contact")
        self.assertEqual(checker.first_failure["tick"], 0)
        self.assertEqual(checker.first_failure["actual"], [0, 0, 1])

    def test_runtime_rejects_missing_required_initial_cell_with_structured_failure(self):
        checker, trace = self._runtime_case(required_cell=2)
        failure = checker.consume(trace, 0, defer_recurrence=True)
        self.assertIn("required initial cell", failure)
        self.assertEqual(checker.first_failure["stage"], "footprint")
        self.assertEqual(checker.first_failure["code"], "required_cell_mismatch")
        self.assertEqual(checker.first_failure["expected"], {"at": [0, 0, 0], "cell": 2})
        self.assertEqual(checker.first_failure["actual"], {"at": [0, 0, 0], "cell": 1})

    def _interleaved_checker(self, order="interleaved"):
        sys.path.insert(0, str(Path.cwd() / "tools"))
        from extension_contract import Contract, Port, PrescribedEvent, CaseChecker
        contract = Contract(
            "interleaved", Path("fixture.flyer"), 4, 1, 1,
            (Port("a", "input", (0, 0, 0), "mw", None, None),
             Port("b", "input", (0, 0, 1), "mw", None, None)),
            prescribed_script=Path("script.txt"), prescribed_order=order,
            prescribed=(PrescribedEvent(0, (0, 0, 0), 1),
                        PrescribedEvent(0, (0, 0, 1), 2)))
        initial = {"initial": [[0, 0, 0, 1], [0, 0, 1, 1]],
                   "initial_owners": [], "steps": []}
        return CaseChecker(contract, initial)

    @staticmethod
    def _interleaved_wrapper(second_limit_load=1, duplicate=False):
        def start(inp, move_id, sources):
            return {"tick": 0, "stage": "prescribed", "action": "prescribed move",
                    "active_input": list(inp), "prescribed_move_id": move_id,
                    "prescribed_order": "interleaved",
                    "movement": {"sources": [list(p) for p in sources],
                                 "destinations": [[p[0] + 1, p[1], p[2]] for p in sources],
                                 "failure": None}}
        starts = [start((0, 0, 1), 0, [(0, 0, 1), (0, 0, 2)]),
                  {"tick": 0, "stage": "piston", "action": "extend",
                   "changes": [[5, 0, 0, 1]], "owners": []},
                  start((0, 0, 0), 1, [(0, 0, 0)] if second_limit_load == 1 else [(0, 0, 0), (0, 0, -1)])]
        if duplicate:
            starts[-1]["active_input"] = [0, 0, 1]
        return {"tick": 0, "prescribed_order": "interleaved", "schedule_seed": 123,
                "pending_before": [], "pending_after": [
                    {"id": 0, "input": [0, 0, 1], "destinations": [[1, 0, 1], [1, 0, 2]]},
                    {"id": 1, "input": [0, 0, 0], "destinations": [[1, 0, 0]] if second_limit_load == 1 else [[1, 0, 0], [1, 0, -1]]}],
                "trace": {"steps": starts}}

    def test_interleaved_matches_reordered_inputs_and_uses_each_event_cap(self):
        checker = self._interleaved_checker()
        self.assertIsNone(checker.validate_prescribed_wrapper(self._interleaved_wrapper(), 0))

        settles = []
        for move_id, inp, positions in (
                (0, (0, 0, 1), [(1, 0, 1), (1, 0, 2)]),
                (1, (0, 0, 0), [(1, 0, 0)])):
            settles.append({"tick": 1, "stage": "prescribed", "action": "settle prescribed move",
                            "active_input": list(inp), "prescribed_move_id": move_id,
                            "prescribed_order": "interleaved",
                            "movement": {"sources": [list(p) for p in positions],
                                         "destinations": [[p[0] + 1, p[1], p[2]] for p in positions],
                                         "failure": None}})
        wrapper = {"tick": 1, "prescribed_order": "interleaved", "schedule_seed": 123,
                   "pending_before": checker._pending_record(checker.pending_prescribed),
                   "pending_after": [],
                   "trace": {"steps": settles + [{"tick": 1, "stage": "chunk", "action": None,
                                                    "changes": [], "owners": []}]}}
        self.assertIsNone(checker.validate_prescribed_wrapper(wrapper, 1))

    def test_interleaved_rejects_missing_or_duplicate_scheduled_action(self):
        checker = self._interleaved_checker()
        missing = self._interleaved_wrapper()
        missing["trace"]["steps"] = missing["trace"]["steps"][:2]
        self.assertIn("expected 2 prescribed", checker.validate_prescribed_wrapper(missing, 0))
        checker = self._interleaved_checker()
        duplicate = self._interleaved_wrapper(duplicate=True)
        self.assertIn("exactly once", checker.validate_prescribed_wrapper(duplicate, 0))
        checker = self._interleaved_checker()
        over_cap = self._interleaved_wrapper(second_limit_load=2)
        self.assertIn("exceeded max_load 1", checker.validate_prescribed_wrapper(over_cap, 0))
        checker = self._interleaved_checker()
        bad_seed = self._interleaved_wrapper()
        bad_seed["schedule_seed"] = -1
        self.assertIn("valid u64 schedule_seed", checker.validate_prescribed_wrapper(bad_seed, 0))

    def test_interleaved_failed_stroke_reports_simulator_overlay(self):
        checker = self._interleaved_checker()
        wrapper = self._interleaved_wrapper()
        failed = wrapper["trace"]["steps"][0]
        failed["action"] = "prescribed move failed"
        failed["movement"]["failure"] = [[0, 0, 1], "missing prescribed input"]
        wrapper["pending_after"] = [wrapper["pending_after"][1]]
        diagnostic = checker.validate_prescribed_wrapper(wrapper, 0)
        self.assertIn("missing prescribed input", diagnostic)
        self.assertEqual(checker.first_failure["code"], "prescribed_move_failed")
        self.assertEqual(checker.first_failure["expected"], {"input": [0, 0, 1], "max_load": 2})
        self.assertEqual(checker.first_failure["actual"]["failure"],
                         [[0, 0, 1], "missing prescribed input"])

    def test_legacy_before_order_still_matches_script_row_order(self):
        checker = self._interleaved_checker(order="before_natural")
        wrapper = self._interleaved_wrapper()
        wrapper.pop("schedule_seed")
        wrapper["prescribed_order"] = "before_natural"
        for step in wrapper["trace"]["steps"]:
            if step.get("stage") == "prescribed":
                step["prescribed_order"] = "before_natural"
        self.assertIn("does not match script", checker.validate_prescribed_wrapper(wrapper, 0))

    def test_base_contract_rejects_deleted_required_cell_before_trace_consumption(self):
        sys.path.insert(0, str(Path.cwd() / "tools"))
        from extension_contract import Contract, ContractError, CaseChecker, Port
        contract = Contract("footprint", Path("fixture.flyer"), 4, 1, 1,
                            (Port("p", "output", (0, 0, 0), "mw", None, None),),
                            required_cells=(((0, 0, 0), 2),))
        initial = {"initial": [[0, 0, 0, 1]], "initial_owners": [], "steps": []}
        with self.assertRaises(ContractError) as caught:
            CaseChecker(contract, initial)
        self.assertEqual(caught.exception.first_failure["code"], "required_cell_mismatch")
        self.assertEqual(caught.exception.first_failure["actual"],
                         {"at": [0, 0, 0], "cell": 1})

    def test_cli_runs_both_orders_and_reports_missing_cell_before_trace(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            tmp_path = Path(tmp)
            for order in ("before_natural", "after_natural"):
                out = tmp_path / order
                with contextlib.redirect_stdout(io.StringIO()):
                    code = main([str(ROOT / "rear_cap_design.json"), "--out-dir", str(out),
                                 "--order", order, "--check"])
                self.assertEqual(code, 0)
                result = json.loads((out / "result.json").read_text(encoding="utf-8"))
                self.assertTrue(result["passed"], result["first_failure"])
            bad = json.loads(json.dumps(self.raw))
            bad["flyer"] = "../candidate.flyer"
            bad["required_cells"][0]["cell"] = 999
            bad_path = tmp_path / "bad_design.json"
            bad_path.write_text(json.dumps(bad), encoding="utf-8")
            out = tmp_path / "bad"
            with contextlib.redirect_stdout(io.StringIO()):
                code = main([str(bad_path), "--out-dir", str(out), "--check"])
            self.assertEqual(code, 1)
            result = json.loads((out / "result.json").read_text(encoding="utf-8"))
            self.assertFalse(result["passed"])
            self.assertEqual(result["first_failure"]["code"], "required_cell_mismatch")
            self.assertEqual(result["case"]["ticks"], 0)

    def test_cli_never_promotes_failed_case_without_diagnostic_to_pass(self):
        sys.path.insert(0, str(Path.cwd() / "tools"))
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            out = Path(tmp) / "mocked"
            with patch("extension_contract.run_case", return_value={
                    "passed": False, "ticks": 3, "diagnostic": "driver exited with status 1",
                    "first_failure": None}), patch("extension_contract._prescribed_driver_path",
                                                    return_value=Path("mock-driver")), \
                    contextlib.redirect_stdout(io.StringIO()):
                code = main([str(ROOT / "rear_cap_design.json"), "--out-dir", str(out), "--check"])
            self.assertEqual(code, 1)
            result = json.loads((out / "result.json").read_text(encoding="utf-8"))
            self.assertFalse(result["passed"])
            self.assertEqual(result["first_failure"]["code"], "contract_failure")
            self.assertEqual(result["first_failure"]["message"], "driver exited with status 1")

    def test_cli_writes_structured_schema_failure_result(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            tmp_path = Path(tmp)
            bad = dict(self.raw)
            bad["unknown"] = True
            source = tmp_path / "drift.json"
            source.write_text(json.dumps(bad), encoding="utf-8")
            out = tmp_path / "schema"
            with contextlib.redirect_stdout(io.StringIO()):
                code = main([str(source), "--out-dir", str(out), "--check"])
            self.assertEqual(code, 2)
            result = json.loads((out / "result.json").read_text(encoding="utf-8"))
            self.assertFalse(result["passed"])
            self.assertEqual(result["first_failure"]["stage"], "schema")
            self.assertEqual(result["first_failure"]["code"], "invalid_design")

    def test_cli_reports_missing_flyer_and_nonobject_as_schema_errors(self):
        missing = dict(self.raw)
        missing.pop("flyer")
        absolute = dict(self.raw, flyer=str((ROOT / "candidate.flyer").resolve()))
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            for i, raw in enumerate((None, [], missing, absolute)):
                source = Path(tmp) / f"bad{i}.json"
                source.write_text(json.dumps(raw), encoding="utf-8")
                out = Path(tmp) / f"out{i}"
                with contextlib.redirect_stdout(io.StringIO()):
                    code = main([str(source), "--out-dir", str(out), "--check"])
                self.assertEqual(code, 2)
                self.assertEqual(json.loads((out / "result.json").read_text())["first_failure"]["stage"], "schema")




if __name__ == '__main__':
    unittest.main()


