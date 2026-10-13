import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from extension_contract import (CaseChecker, Contract, ContractError, DriveEvent, Port,
                                PrescribedEvent,
                                load_contract, run_case)


def contract(*ports, advance=1, period=2, recurrence="exact", boundary_envelope=None):
    return Contract("test", Path("fixture.flyer"), period, advance, 1, tuple(ports),
                    recurrence, boundary_envelope)


def trace0():
    return {
        "initial": [[0, 0, 0, 1], [1, 0, 0, 1]], "initial_owners": [],
        "steps": [],
    }


def moving_tick():
    row = trace0()
    row["steps"] = [{
        "tick": 0, "action": "extend", "active_piston": [0, 0, -1],
        "movement": {"sources": [[0, 0, 0], [1, 0, 0]],
                     "destinations": [[1, 0, 0], [2, 0, 0]], "failure": None},
        "changes": [[0, 0, 0, None], [1, 0, 0, 17], [2, 0, 0, 17]], "owners": [],
    }]
    return row


class ExtensionContractTests(unittest.TestCase):
    def prescribed_contract(self, *, limit=1):
        return Contract("prescribed-test", Path("fixture.flyer"), 2, 1, 1,
                        (Port("feed", "input", (0, 0, 0), "m", (1,), (0,)),),
                        prescribed_script=Path("script.txt"), prescribed_order="before_natural",
                        prescribed=(PrescribedEvent(0, (0, 0, 0), limit),))

    def prescribed_start_wrapper(self, *, sources=None, destinations=None, pending=None,
                                 changes=None, duplicate=False):
        sources = [[0, 0, 0]] if sources is None else sources
        destinations = [[1, 0, 0]] if destinations is None else destinations
        pending = [{"id": 0, "input": [0, 0, 0], "destinations": destinations}] if pending is None else pending
        step = {"tick": 0, "stage": "prescribed", "action": "prescribed move",
                "active_input": [0, 0, 0], "prescribed_move_id": 0,
                "prescribed_order": "before_natural",
                "movement": {"sources": sources, "destinations": destinations, "failure": None},
                "changes": ([[0, 0, 0, None], [1, 0, 0, 17]] if changes is None else changes),
                "owners": []}
        steps = [step, dict(step)] if duplicate else [step]
        steps.append({"tick": 0, "stage": "chunk", "action": None,
                      "changes": [], "owners": []})
        return {"tick": 0, "prescribed_order": "before_natural", "pending_before": [],
                "pending_after": pending,
                "trace": {"initial": [[0, 0, 0, 1]], "initial_owners": [], "steps": steps}}

    def prescribed_settle_wrapper(self, *, pending_before=None, changes=None):
        pending = [{"id": 0, "input": [0, 0, 0], "destinations": [[1, 0, 0]]}]
        step = {"tick": 1, "stage": "prescribed", "action": "settle prescribed move",
                "active_input": [0, 0, 0], "prescribed_move_id": 0,
                "prescribed_order": "before_natural",
                "movement": {"sources": [[1, 0, 0]], "destinations": [], "failure": None},
                "changes": ([[1, 0, 0, 1]] if changes is None else changes), "owners": []}
        chunk = {"tick": 1, "stage": "chunk", "action": None, "changes": [], "owners": []}
        return {"tick": 1, "prescribed_order": "before_natural",
                "pending_before": pending if pending_before is None else pending_before,
                "pending_after": [],
                "trace": {"initial": [[1, 0, 0, 17]], "initial_owners": [], "steps": [step, chunk]}}

    def test_prescribed_mode_tracks_start_then_settlement_without_second_translation(self):
        checker = CaseChecker(self.prescribed_contract(), trace0() | {
            "initial": [[0, 0, 0, 1]]})
        start = self.prescribed_start_wrapper()
        self.assertIsNone(checker.validate_prescribed_wrapper(start, 0))
        self.assertIsNone(checker.consume(start["trace"], 0, defer_recurrence=True))
        self.assertEqual(checker.ids[checker.port_ids["feed"]], (1, 0, 0))
        settle = self.prescribed_settle_wrapper()
        self.assertIsNone(checker.validate_prescribed_wrapper(settle, 1))
        self.assertIsNone(checker.consume(settle["trace"], 1, defer_recurrence=True))
        self.assertEqual(checker.ids[checker.port_ids["feed"]], (1, 0, 0))
        self.assertEqual(checker.cells[(1, 0, 0)], 1)
        self.assertIsNone(checker.check_boundary(1))

    def test_prescribed_mode_rejects_forged_ledger_source_deletion_duplicate_and_cap(self):
        for label, wrapper, limit, expected in (
                ("pending", self.prescribed_start_wrapper(pending=[{"id": 0, "input": [0, 0, 0],
                    "destinations": [[2, 0, 0]]}]), 1, "pending_after"),
                ("source", self.prescribed_start_wrapper(sources=[[3, 0, 0]]), 1, "omitted input"),
                ("delete", self.prescribed_start_wrapper(changes=[[0, 0, 0, None]]), 1, "deleted"),
                ("duplicate", self.prescribed_start_wrapper(duplicate=True), 1, "expected 1 prescribed"),
                ("cap", self.prescribed_start_wrapper(sources=[[0, 0, 0], [4, 0, 0]],
                    destinations=[[1, 0, 0], [5, 0, 0]]), 1, "exceeded max_load")):
            with self.subTest(label=label):
                checker = CaseChecker(self.prescribed_contract(limit=limit), {"initial": [[0, 0, 0, 1]],
                                                                              "initial_owners": [], "steps": []})
                failure = checker.validate_prescribed_wrapper(wrapper, 0)
                if failure is None:
                    failure = checker.consume(wrapper["trace"], 0, defer_recurrence=True)
                self.assertIn(expected, failure)

    def test_prescribed_settlement_requires_matching_pending_identity_and_sources(self):
        checker = CaseChecker(self.prescribed_contract(), {"initial": [[0, 0, 0, 1]],
                                                            "initial_owners": [], "steps": []})
        start = self.prescribed_start_wrapper()
        self.assertIsNone(checker.validate_prescribed_wrapper(start, 0))
        forged = self.prescribed_settle_wrapper(pending_before=[{"id": 7, "input": [0, 0, 0],
                                                                  "destinations": [[1, 0, 0]]}])
        self.assertIn("pending_before differs", checker.validate_prescribed_wrapper(forged, 1))

    def test_prescribed_same_tick_independent_moves_use_ordered_pending_ledger(self):
        events = (PrescribedEvent(0, (0, 0, 0), 1), PrescribedEvent(0, (10, 0, 0), 1))
        spec = Contract("two-inputs", Path("fixture.flyer"), 2, 1, 1,
                        (Port("left", "input", (0, 0, 0), "m", (1,), (0,)),
                         Port("right", "input", (10, 0, 0), "m", (1,), (0,))),
                        prescribed_script=Path("script.txt"), prescribed_order="before_natural",
                        prescribed=events)
        initial = {"initial": [[0, 0, 0, 4], [10, 0, 0, 4]], "initial_owners": [], "steps": []}
        checker = CaseChecker(spec, initial)
        pending = [
            {"id": 0, "input": [0, 0, 0], "destinations": [[1, 0, 0]]},
            {"id": 1, "input": [10, 0, 0], "destinations": [[11, 0, 0]]},
        ]
        starts = []
        for move_id, (source, destination, input_pos) in enumerate(
                (([0, 0, 0], [1, 0, 0], [0, 0, 0]),
                 ([10, 0, 0], [11, 0, 0], [10, 0, 0]))):
            starts.append({"tick": 0, "stage": "prescribed", "action": "prescribed move",
                           "active_input": input_pos, "prescribed_move_id": move_id,
                           "prescribed_order": "before_natural",
                           "movement": {"sources": [source], "destinations": [destination], "failure": None},
                           "changes": [[*source, None], [*destination, 20]], "owners": []})
        start_wrapper = {"tick": 0, "prescribed_order": "before_natural", "pending_before": [],
                        "pending_after": pending,
                        "trace": {"initial": initial["initial"], "initial_owners": [],
                                  "steps": starts + [{"tick": 0, "stage": "chunk", "action": None,
                                                      "changes": [], "owners": []}]}}
        self.assertIsNone(checker.validate_prescribed_wrapper(start_wrapper, 0))
        self.assertIsNone(checker.consume(start_wrapper["trace"], 0, defer_recurrence=True))
        settles = []
        for move_id, (input_pos, source) in enumerate(
                (([0, 0, 0], [1, 0, 0]), ([10, 0, 0], [11, 0, 0]))):
            settles.append({"tick": 1, "stage": "prescribed", "action": "settle prescribed move",
                            "active_input": input_pos, "prescribed_move_id": move_id,
                            "prescribed_order": "before_natural",
                            "movement": {"sources": [source], "destinations": [], "failure": None},
                            "changes": [[*source, 4]], "owners": []})
        settle_wrapper = {"tick": 1, "prescribed_order": "before_natural", "pending_before": pending,
                          "pending_after": [],
                          "trace": {"initial": [[1, 0, 0, 20], [11, 0, 0, 20]],
                                    "initial_owners": [], "steps": settles + [
                                        {"tick": 1, "stage": "chunk", "action": None,
                                         "changes": [], "owners": []}]}}
        self.assertIsNone(checker.validate_prescribed_wrapper(settle_wrapper, 1))
        self.assertIsNone(checker.consume(settle_wrapper["trace"], 1, defer_recurrence=True))

    def test_prescribed_same_tick_overlapping_closures_are_rejected(self):
        spec = Contract("overlap", Path("fixture.flyer"), 2, 1, 1,
                        (Port("a", "input", (0, 0, 0), "m", None, None),
                         Port("b", "input", (2, 0, 0), "m", None, None)),
                        prescribed_script=Path("script.txt"), prescribed_order="before_natural",
                        prescribed=(PrescribedEvent(0, (0, 0, 0), 2),
                                    PrescribedEvent(0, (2, 0, 0), 2)))
        checker = CaseChecker(spec, {"initial": [[0, 0, 0, 1], [2, 0, 0, 1]],
                                     "initial_owners": [], "steps": []})
        wrapper = {"tick": 0, "prescribed_order": "before_natural", "pending_before": [],
                   "pending_after": [], "trace": {"initial": [[0, 0, 0, 1], [2, 0, 0, 1]],
                   "initial_owners": [], "steps": [
                       {"tick": 0, "stage": "prescribed", "action": "prescribed move",
                        "active_input": [0, 0, 0], "prescribed_move_id": 0,
                        "prescribed_order": "before_natural",
                        "movement": {"sources": [[0, 0, 0], [2, 0, 0]],
                                     "destinations": [[1, 0, 0], [3, 0, 0]], "failure": None},
                        "changes": [], "owners": []},
                       {"tick": 0, "stage": "prescribed", "action": "prescribed move",
                        "active_input": [2, 0, 0], "prescribed_move_id": 1,
                        "prescribed_order": "before_natural",
                        "movement": {"sources": [[2, 0, 0]], "destinations": [[3, 0, 0]], "failure": None},
                        "changes": [], "owners": []},
                       {"tick": 0, "stage": "chunk", "action": None, "changes": [], "owners": []}]}}
        self.assertIn("closures overlap", checker.validate_prescribed_wrapper(wrapper, 0))

    def test_prescribed_ledger_rejects_missing_duplicate_settlement_and_natural_piston_order(self):
        checker = CaseChecker(self.prescribed_contract(), {"initial": [[0, 0, 0, 1]],
                                                            "initial_owners": [], "steps": []})
        self.assertIsNone(checker.validate_prescribed_wrapper(self.prescribed_start_wrapper(), 0))
        missing = self.prescribed_settle_wrapper()
        missing["trace"]["steps"] = [missing["trace"]["steps"][-1]]
        self.assertIn("expected 1 prescribed", checker.validate_prescribed_wrapper(missing, 1))
        duplicate = self.prescribed_settle_wrapper()
        duplicate["trace"]["steps"].insert(1, dict(duplicate["trace"]["steps"][0]))
        self.assertIn("expected 1 prescribed", checker.validate_prescribed_wrapper(duplicate, 1))

        settle_after_piston = self.prescribed_settle_wrapper()
        settle_action, chunk = settle_after_piston["trace"]["steps"]
        settle_after_piston["trace"]["steps"] = [
            {"tick": 1, "stage": "piston", "action": "finish extension",
             "changes": [], "owners": []},
            settle_action,
            chunk,
        ]
        self.assertIn("settlement did not occur before natural processing",
                      checker.validate_prescribed_wrapper(settle_after_piston, 1))

        for order, expected in (("before_natural", "before natural"), ("after_natural", "after natural")):
            spec = Contract("order", Path("fixture.flyer"), 2, 1, 1,
                            (Port("feed", "input", (0, 0, 0), "m", None, None),),
                            prescribed_script=Path("script.txt"), prescribed_order=order,
                            prescribed=(PrescribedEvent(0, (0, 0, 0), 1),))
            c = CaseChecker(spec, {"initial": [[0, 0, 0, 1]], "initial_owners": [], "steps": []})
            wrapper = self.prescribed_start_wrapper()
            wrapper["prescribed_order"] = order
            wrapper["pending_after"][0]["id"] = 0
            action = wrapper["trace"]["steps"][0]
            action["prescribed_order"] = order
            if order == "before_natural":
                wrapper["trace"]["steps"] = [wrapper["trace"]["steps"][-1],
                                              {"tick": 0, "stage": "piston", "action": "extend",
                                               "changes": [], "owners": []}, action]
            else:
                wrapper["trace"]["steps"] = [wrapper["trace"]["steps"][-1], action,
                                              {"tick": 0, "stage": "piston", "action": "extend",
                                               "changes": [], "owners": []}]
            self.assertIn(expected, c.validate_prescribed_wrapper(wrapper, 0))

    def test_prescribed_contract_requires_order_and_declared_input_at_tick_position(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "script.txt").write_text("0 0 0 0 1\n", encoding="utf-8")
            raw = {"version": 1, "name": "prescribed", "flyer": "driver.flyer",
                   "period_ticks": 2, "advance": 1, "cycles": 1,
                   "prescribed_script": "script.txt", "prescribed_order": "before_natural",
                   "ports": [{"name": "in", "role": "input", "at": [0, 0, 0], "word": "m"}]}
            contract_path = base / "contract.json"
            contract_path.write_text(json.dumps(raw), encoding="utf-8")
            self.assertEqual(load_contract(contract_path).prescribed_order, "before_natural")
            for update, message in (({"prescribed_order": None}, "prescribed_order"),
                                    ({"prescribed_order": "before"}, "before_natural"),
                                    ({"ports": [{"name": "in", "role": "input",
                                                 "at": [1, 0, 0], "word": "m"}]},
                                     "expected phase coordinate")):
                with self.subTest(message=message):
                    changed = dict(raw)
                    changed.update(update)
                    contract_path.write_text(json.dumps(changed), encoding="utf-8")
                    with self.assertRaisesRegex(ContractError, message):
                        load_contract(contract_path)

    def test_real_prescribed_primitive_backend_on_three_glue_calibration(self):
        from extension_contract import _prescribed_driver_path

        try:
            driver = _prescribed_driver_path()
        except ContractError:
            self.skipTest("build target/release/extension-prescribe to run integration test")
        path = ROOT / "flyers" / "WIP" / "experiments" / "extension_contract_20261011" / \
            "prescribed_primitive" / "contracts" / "mmmww_before.json"
        if not path.is_file():
            self.skipTest("prescribed primitive calibration fixture is not present")
        spec = load_contract(path)
        result = run_case(spec, driver, None)
        self.assertTrue(result["passed"], result["diagnostic"])
        self.assertEqual(result["ticks"], spec.period_ticks * spec.cycles)
        self.assertEqual(result["whole_assembly_max_action"], 3)
        self.assertEqual(result["input_max_action_loads"]["driver"], [3, 3, 3, None, None])

    def test_real_same_tick_two_independent_prescribed_inputs(self):
        from fastflyer import Block, Flyer, Kind
        from extension_contract import _prescribed_driver_path

        try:
            driver = _prescribed_driver_path()
        except ContractError:
            self.skipTest("build target/release/extension-prescribe to run integration test")
        with tempfile.TemporaryDirectory(dir=ROOT / "target") as temp:
            base = Path(temp)
            fixture = base / "two_inputs.flyer"
            script = base / "two_inputs.txt"
            flyer = Flyer()
            flyer.set((0, 0, 0), Block(Kind.SMOOTH_STONE))
            flyer.set((10, 0, 0), Block(Kind.SMOOTH_STONE))
            flyer.save(fixture)
            script.write_text("0 0 0 0 1\n0 10 0 0 1\n", encoding="utf-8")
            spec = Contract("two-independent-inputs", fixture, 2, 1, 1,
                            (Port("left", "input", (0, 0, 0), "m", (1,), (0,)),
                             Port("right", "input", (10, 0, 0), "m", (1,), (0,))),
                            prescribed_script=script, prescribed_order="before_natural",
                            prescribed=(PrescribedEvent(0, (0, 0, 0), 1),
                                        PrescribedEvent(0, (10, 0, 0), 1)))
            result = run_case(spec, driver, None)
        self.assertTrue(result["passed"], result["diagnostic"])
        self.assertEqual(result["ticks"], 2)
        self.assertEqual(result["input_max_action_loads"], {"left": [1], "right": [1]})

    def test_real_same_tick_inputs_have_independent_caps(self):
        from fastflyer import Block, Flyer, Kind
        from extension_contract import _prescribed_driver_path
        try:
            driver = _prescribed_driver_path()
        except ContractError:
            self.skipTest("build extension-prescribe for integration tests")
        with tempfile.TemporaryDirectory(dir=ROOT / "target") as temp:
            base = Path(temp)
            fixture, script = base / "different_caps.flyer", base / "drive.txt"
            flyer = Flyer()
            for x in (0, 10, 11):
                flyer.set((x, 0, 0), Block(Kind.SMOOTH_STONE))
            flyer.save(fixture)
            script.write_text("0 0 0 0 1\n0 10 0 0 2\n", encoding="utf-8")
            spec = Contract("independent-caps", fixture, 2, 1, 1,
                            (Port("single", "input", (0, 0, 0), "m", (1,), (0,)),
                             Port("pair", "input", (10, 0, 0), "m", (2,), (0,))),
                            prescribed_script=script, prescribed_order="before_natural",
                            prescribed=(PrescribedEvent(0, (0, 0, 0), 1),
                                        PrescribedEvent(0, (10, 0, 0), 2)))
            result = run_case(spec, driver, None)
        self.assertTrue(result["passed"], result["diagnostic"])
        self.assertEqual(result["input_max_action_loads"], {"single": [1], "pair": [2]})

    def test_real_ordered_prescribed_inputs_can_reuse_vacated_cell(self):
        from fastflyer import Block, Flyer, Kind
        from extension_contract import _prescribed_driver_path

        try:
            driver = _prescribed_driver_path()
        except ContractError:
            self.skipTest("build target/release/extension-prescribe to run integration test")
        with tempfile.TemporaryDirectory(dir=ROOT / "target") as temp:
            base = Path(temp)
            fixture, script = base / "adjacent.flyer", base / "adjacent.txt"
            flyer = Flyer()
            flyer.set((0, 0, 0), Block(Kind.SMOOTH_STONE))
            flyer.set((1, 0, 0), Block(Kind.SMOOTH_STONE))
            flyer.save(fixture)
            script.write_text("0 1 0 0 1\n0 0 0 0 1\n", encoding="utf-8")
            spec = Contract("ordered-vacancy", fixture, 2, 1, 1,
                            (Port("rear", "input", (0, 0, 0), "m", (1,), (0,)),
                             Port("front", "input", (1, 0, 0), "m", (1,), (0,))),
                            prescribed_script=script, prescribed_order="before_natural",
                            prescribed=(PrescribedEvent(0, (1, 0, 0), 1),
                                        PrescribedEvent(0, (0, 0, 0), 1)))
            result = run_case(spec, driver, None)
        self.assertTrue(result["passed"], result["diagnostic"])
        self.assertEqual(result["input_max_action_loads"], {"rear": [1], "front": [1]})

    def test_real_mixed_rear_cap_preserves_exact_recurrence(self):
        from extension_contract import _prescribed_driver_path
        try:
            driver = _prescribed_driver_path()
        except ContractError:
            self.skipTest("build target/release/extension-prescribe to run integration test")
        base = ROOT / "flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap"
        for order in ("before_natural", "after_natural"):
            with self.subTest(order=order):
                spec = load_contract(base / f"mixed_{order}_contract.json")
                self.assertEqual(spec.recurrence, "exact")
                result = run_case(spec, driver, None)
                self.assertTrue(result["passed"], result["diagnostic"])
                self.assertEqual(result["input_max_action_loads"],
                                 {"redstone_input": [1, 1, None, None],
                                  "k1_input": [None, None, 6, 6]})
                self.assertEqual(result["whole_assembly_max_action"], 7)

    def test_drive_wrapper_edits_are_scripted_and_candidate_moves(self):
        initial = {"initial": [[0, 0, 0, 1]], "initial_owners": [], "steps": []}
        spec = Contract("drive-test", Path("fixture.flyer"), 4, 1, 1,
                        (Port("out", "input", (0, 0, 0), "mw", None, None),),
                        drive_script=Path("drive.txt"),
                        drives=(DriveEvent(0, (0, 0, 0), 1),))
        checker = CaseChecker(spec, initial)
        wrapper = {"tick": 0, "fixture_before": [[-1, 0, 0, 9], [-2, 0, 0, 6]],
                   "fixture_after": [],
                   "trace": {"initial": [[-2, 0, 0, 6], [-1, 0, 0, 9], [0, 0, 0, 1]],
                             "initial_owners": [], "steps": [{
                                 "tick": 0, "action": "extend", "active_piston": [-1, 0, 0],
                                 "movement": {"sources": [[0, 0, 0]], "destinations": [[1, 0, 0]],
                                              "failure": None},
                                 "changes": [[0, 0, 0, 10], [1, 0, 0, 17]], "owners": []}]}}
        self.assertIsNone(checker.prepare_external_before(wrapper, 0))
        self.assertIsNone(checker.consume(wrapper["trace"], 0, defer_recurrence=True))
        self.assertIsNone(checker.finish_external_after(wrapper, 0))
        self.assertEqual(checker.cells, {(0, 0, 0): 10, (1, 0, 0): 17,
                                         (-2, 0, 0): 6, (-1, 0, 0): 9})

    def test_drive_wrapper_rejects_undeclared_edits_and_candidate_overwrite(self):
        initial = {"initial": [[-1, 0, 0, 1], [0, 0, 0, 1]], "initial_owners": [], "steps": []}
        spec = Contract("drive-test", Path("fixture.flyer"), 4, 1, 1,
                        (Port("out", "input", (0, 0, 0), "mw", None, None),),
                        drive_script=Path("drive.txt"),
                        drives=(DriveEvent(0, (0, 0, 0), 1),))
        checker = CaseChecker(spec, initial)
        wrapper = {"tick": 0, "fixture_before": [[-1, 0, 0, 9], [-2, 0, 0, 6],
                                                     [0, 0, 0, None]],
                   "fixture_after": [], "trace": {}}
        self.assertIn("fixture_before edits differ", checker.prepare_external_before(wrapper, 0))
        wrapper["fixture_before"] = [[-1, 0, 0, 9], [-2, 0, 0, 6]]
        self.assertIn("overwrite occupied cell", checker.prepare_external_before(wrapper, 0))

    def test_external_fixture_cannot_be_a_movement_source(self):
        initial = {"initial": [[0, 0, 0, 1]], "initial_owners": [], "steps": []}
        spec = Contract("drive-test", Path("fixture.flyer"), 4, 1, 1,
                        (Port("out", "input", (0, 0, 0), "mw", None, None),),
                        drive_script=Path("drive.txt"),
                        drives=(DriveEvent(0, (0, 0, 0), 2),))
        checker = CaseChecker(spec, initial)
        wrapper = {"tick": 0, "fixture_before": [[-1, 0, 0, 9], [-2, 0, 0, 6]],
                   "fixture_after": [],
                   "trace": {"initial": [[-2, 0, 0, 6], [-1, 0, 0, 9], [0, 0, 0, 1]],
                             "initial_owners": [], "steps": [{
                                 "tick": 0, "action": "extend", "active_piston": [-1, 0, 0],
                                 "movement": {"sources": [[-1, 0, 0], [0, 0, 0]],
                                              "destinations": [[0, 0, 0], [1, 0, 0]],
                                              "failure": None},
                                 "changes": [[-1, 0, 0, None], [0, 0, 0, 17], [1, 0, 0, 17]],
                                 "owners": []}]}}
        self.assertIsNone(checker.prepare_external_before(wrapper, 0))
        self.assertIn("moved external fixture source", checker.consume(wrapper["trace"], 0,
                                                                         defer_recurrence=True))

    def test_external_piston_arm_cannot_be_a_movement_source(self):
        initial = {"initial": [[0, 0, 0, 1]], "initial_owners": [], "steps": []}
        spec = Contract("drive-test", Path("fixture.flyer"), 4, 1, 1,
                        (Port("out", "input", (0, 0, 0), "mw", None, None),),
                        drive_script=Path("drive.txt"),
                        drives=(DriveEvent(0, (0, 0, 0), 1),))
        checker = CaseChecker(spec, initial)
        wrapper = {"tick": 0, "fixture_before": [[-1, 0, 0, 9], [-2, 0, 0, 6]],
                   "fixture_after": [],
                   "trace": {"initial": [[-2, 0, 0, 6], [-1, 0, 0, 9], [0, 0, 0, 1]],
                             "initial_owners": [], "steps": [
                                 {"tick": 0, "action": "extend", "active_piston": [-1, 0, 0],
                                  "movement": {"sources": [[0, 0, 0]], "destinations": [[1, 0, 0]],
                                               "failure": None},
                                  "changes": [[0, 0, 0, 10], [1, 0, 0, 17]], "owners": []},
                                 {"tick": 0, "action": "extend", "active_piston": [0, 0, -1],
                                  "movement": {"sources": [[0, 0, 0]], "destinations": [[1, 0, 0]],
                                               "failure": None},
                                  "changes": [], "owners": []},
                             ]}}
        self.assertIsNone(checker.prepare_external_before(wrapper, 0))
        self.assertIn("moved external fixture source", checker.consume(
            wrapper["trace"], 0, defer_recurrence=True))

    def test_external_piston_arm_cannot_disappear_before_retraction(self):
        initial = {"initial": [[0, 0, 0, 1]], "initial_owners": [], "steps": []}
        spec = Contract("drive-test", Path("fixture.flyer"), 4, 1, 1,
                        (Port("out", "input", (0, 0, 0), "mw", None, None),),
                        drive_script=Path("drive.txt"),
                        drives=(DriveEvent(0, (0, 0, 0), 1),))
        checker = CaseChecker(spec, initial)
        wrapper = {"tick": 0, "fixture_before": [[-1, 0, 0, 9], [-2, 0, 0, 6]],
                   "fixture_after": [],
                   "trace": {"initial": [[-2, 0, 0, 6], [-1, 0, 0, 9], [0, 0, 0, 1]],
                             "initial_owners": [], "steps": [
                                 {"tick": 0, "action": "extend", "active_piston": [-1, 0, 0],
                                  "movement": {"sources": [[0, 0, 0]], "destinations": [[1, 0, 0]],
                                               "failure": None},
                                  "changes": [[0, 0, 0, 10], [1, 0, 0, 17]], "owners": []},
                                 {"tick": 0, "action": "idle", "movement": None,
                                  "changes": [[0, 0, 0, None]], "owners": []},
                             ]}}
        self.assertIsNone(checker.prepare_external_before(wrapper, 0))
        self.assertIn("outside its scheduled retraction", checker.consume(
            wrapper["trace"], 0, defer_recurrence=True))

    def test_drive_script_parser_rejects_malformed_rows_and_lifecycle(self):
        contract_path = ROOT / "tests" / "bad_extension_contract.json"
        script_path = ROOT / "tests" / "bad_drive_script.txt"
        base = ('"version":1,"name":"bad","flyer":"x.flyer",'
                '"period_ticks":6,"advance":1,"cycles":2,'
                '"ports":[{"name":"o","role":"output","at":[0,0,0],"word":"mww"}],'
                '"drive_script":"bad_drive_script.txt"')
        cases = [
            ("not a row", "expected five integer columns"),
            ("1 0 0 0 1", "must be even"),
            ("0 0 0 0 0", "minimum 1"),
            ("4 0 0 0 1", "lifecycle crosses a period"),
            ("0 0 0 0 1\n0 0 0 0 2", "duplicate drive event"),
        ]
        try:
            for row, message in cases:
                script_path.write_text(row + "\n", encoding="utf-8")
                contract_path.write_text("{" + base + "}", encoding="utf-8")
                with self.subTest(message=message), self.assertRaisesRegex(ContractError, message):
                    load_contract(contract_path)
        finally:
            contract_path.unlink(missing_ok=True)
            script_path.unlink(missing_ok=True)

    def test_simultaneous_adjacent_same_kind_identity_movement(self):
        checker = CaseChecker(contract(
            Port("a", "output", (0, 0, 0), "m", None, None),
            Port("b", "output", (1, 0, 0), "m", None, None)), trace0())
        self.assertIsNone(checker.consume(moving_tick(), 0))
        self.assertEqual({(identity, pos) for identity, pos in checker.ids.items()},
                         {(0, (1, 0, 0)), (1, (2, 0, 0))})
        settle = {"tick": 1, "initial": [[1, 0, 0, 17], [2, 0, 0, 17]], "initial_owners": [],
                  "steps": [{"tick": 1, "action": "finish extension", "movement": None,
                             "changes": [[1, 0, 0, 1], [2, 0, 0, 1]], "owners": []}]}
        self.assertIsNone(checker.consume(settle, 1))

    def test_too_low_input_budget_fails_with_source_count(self):
        checker = CaseChecker(contract(
            Port("feed", "input", (0, 0, 0), "m", (1,), (0,))), trace0())
        failure = checker.consume(moving_tick(), 0)
        self.assertIn("moved 2 sources, baseline 1 + spare 0 = 1", failure)
        self.assertIn("actor=[0, 0, -1]", failure)
        self.assertEqual(checker.input_max_action_loads["feed"], [2])
        self.assertEqual(checker.whole_assembly_max_action, 2)
        self.assertEqual(checker.first_failure["code"], "input_budget_exceeded")
        self.assertEqual(checker.first_failure["expected"], 1)
        self.assertEqual(checker.first_failure["actual"]["load"], 2)
        self.assertEqual(checker.first_failure["actual"]["sources"], [[0, 0, 0], [1, 0, 0]])

    def test_input_budget_is_checked_only_for_the_containing_action(self):
        initial = {"initial": [[0, 0, 0, 1], [10, 0, 0, 1], [11, 0, 0, 1]],
                   "initial_owners": [], "steps": []}
        checker = CaseChecker(contract(
            Port("feed", "input", (0, 0, 0), "m", (1,), (0,))), initial)
        row = {"initial": initial["initial"], "initial_owners": [], "steps": [
            {"tick": 0, "action": "extend", "movement": {
                "sources": [[0, 0, 0]], "destinations": [[1, 0, 0]], "failure": None},
             "changes": [[0, 0, 0, None], [1, 0, 0, 17]], "owners": []},
            {"tick": 0, "action": "extend", "movement": {
                "sources": [[10, 0, 0], [11, 0, 0]],
                "destinations": [[11, 0, 0], [12, 0, 0]], "failure": None},
             "changes": [[10, 0, 0, None], [11, 0, 0, 17], [12, 0, 0, 17]], "owners": []},
        ]}
        self.assertIsNone(checker.consume(row, 0))
        self.assertEqual(checker.input_max_action_loads["feed"], [1])
        self.assertEqual(checker.whole_assembly_max_action, 2)

    def test_untagged_hardware_identity_may_move_twice_in_one_tick(self):
        initial = {"initial": [[0, 0, 0, 1], [10, 0, 0, 1]],
                   "initial_owners": [], "steps": []}
        checker = CaseChecker(contract(
            Port("tagged", "output", (0, 0, 0), "m", None, None)), initial)
        row = {"initial": initial["initial"], "initial_owners": [], "steps": [
            {"tick": 0, "action": "extend", "active_piston": [0, 0, -1], "movement": {
                "sources": [[0, 0, 0]], "destinations": [[1, 0, 0]], "failure": None},
             "changes": [[0, 0, 0, None], [1, 0, 0, 17]], "owners": []},
            {"tick": 0, "action": "extend", "active_piston": [10, 0, -1], "movement": {
                "sources": [[10, 0, 0]], "destinations": [[11, 0, 0]], "failure": None},
             "changes": [[10, 0, 0, None], [11, 0, 0, 17]], "owners": []},
            {"tick": 0, "action": "extend", "active_piston": [11, 0, -1], "movement": {
                "sources": [[11, 0, 0]], "destinations": [[12, 0, 0]], "failure": None},
             "changes": [[11, 0, 0, None], [12, 0, 0, 17]], "owners": []},
        ]}
        self.assertIsNone(checker.consume(row, 0))
        self.assertEqual(checker.ids[checker.port_ids["tagged"]], (1, 0, 0))
        untagged_id = next(i for i in checker.ids if i != checker.port_ids["tagged"])
        self.assertEqual(checker.ids[untagged_id], (12, 0, 0))

    def test_wrong_output_word_is_rejected(self):
        checker = CaseChecker(contract(
            Port("out", "output", (0, 0, 0), "w", None, None)), trace0())
        self.assertIn("port out expected wait", checker.consume(moving_tick(), 0))
        self.assertEqual(checker.first_failure["code"], "port_motion_mismatch")
        self.assertEqual(checker.first_failure["port"], "out")

    def test_permanent_deletion_is_rejected(self):
        checker = CaseChecker(contract(
            Port("out", "output", (0, 0, 0), "m", None, None)), trace0())
        row = trace0()
        row["steps"] = [{"tick": 0, "action": "idle", "movement": None,
                         "changes": [[0, 0, 0, None]], "owners": []}]
        self.assertIn("permanent identity", checker.consume(row, 0))

    def test_exact_recurrence_checks_cells_and_owner_lists(self):
        checker = CaseChecker(contract(
            Port("out", "output", (0, 0, 0), "m", None, None)), trace0())
        self.assertIsNone(checker.consume(moving_tick(), 0))
        settle = {"tick": 1, "initial": [[1, 0, 0, 17], [2, 0, 0, 17]], "initial_owners": [],
                  "steps": [{"tick": 1, "action": "finish extension", "movement": None,
                             "changes": [[1, 0, 0, 1], [2, 0, 0, 1]],
                             "owners": [[[2, 0, 0], [3, 0, 0]]]}]}
        self.assertIn("owner recurrence mismatch", checker.consume(settle, 1))

    def test_exact_recurrence_checks_encoded_cell_state(self):
        initial = trace0()
        initial["initial"].append([5, 0, 0, 7])  # an observer outside the tagged ports
        checker = CaseChecker(contract(
            Port("out", "output", (0, 0, 0), "m", None, None)), initial)
        moved = moving_tick()
        moved["initial"].append([5, 0, 0, 7])
        self.assertIsNone(checker.consume(moved, 0))
        settle = {"tick": 1, "initial": [[1, 0, 0, 17], [2, 0, 0, 17], [5, 0, 0, 7]],
                  "initial_owners": [],
                  "steps": [{"tick": 1, "action": "finish extension", "movement": None,
                             "changes": [[1, 0, 0, 1], [2, 0, 0, 1], [5, 0, 0, 263]],
                             "owners": []}]}
        self.assertIn("recurrence mismatch", checker.consume(settle, 1))

    def test_nonempty_owner_recurrence_translates_all_three_coordinates(self):
        initial = {"initial": [[0, 0, 0, 9], [2, 0, 0, 1]],
                   "initial_owners": [[[0, 0, 0], [4, 2, 3]]], "steps": []}
        checker = CaseChecker(contract(
            Port("out", "output", (2, 0, 0), "m", None, None)), initial)
        start = {"initial": initial["initial"], "initial_owners": initial["initial_owners"],
                 "steps": [{"tick": 0, "action": "extend", "movement": {
                     "sources": [[0, 0, 0], [2, 0, 0]],
                     "destinations": [[1, 0, 0], [3, 0, 0]], "failure": None},
                     "changes": [[0, 0, 0, None], [1, 0, 0, 25],
                                 [2, 0, 0, None], [3, 0, 0, 17]],
                     "owners": [[[1, 0, 0], [5, 2, 3]]]}]}
        self.assertIsNone(checker.consume(start, 0))
        finish = {"initial": [[1, 0, 0, 25], [3, 0, 0, 17]],
                  "initial_owners": [[[1, 0, 0], [5, 2, 3]]],
                  "steps": [{"tick": 1, "action": "finish extension", "movement": None,
                             "changes": [[1, 0, 0, 9], [3, 0, 0, 1]],
                             "owners": [[[1, 0, 0], [5, 2, 3]]]}]}
        self.assertIsNone(checker.consume(finish, 1))

    def test_bounded_mode_accepts_nonrecurrent_state_inside_envelope(self):
        lower, upper = (0, 0, 0), (1, 0, 2)
        initial = {"initial": [[0, 0, 0, 1], [1, 0, 2, 7]],
                   "initial_owners": [], "steps": []}
        checker = CaseChecker(contract(
            Port("out", "output", (0, 0, 0), "m", None, None),
            recurrence="bounded", boundary_envelope=(lower, upper)), initial)
        start = {"initial": initial["initial"], "initial_owners": [],
                 "steps": [{"tick": 0, "action": "extend", "movement": {
                     "sources": [[0, 0, 0]], "destinations": [[1, 0, 0]], "failure": None},
                     "changes": [[0, 0, 0, None], [1, 0, 0, 17]], "owners": []}]}
        self.assertIsNone(checker.consume(start, 0))
        finish = {"initial": [[1, 0, 0, 17], [1, 0, 2, 7]], "initial_owners": [],
                  "steps": [{"tick": 1, "action": "finish extension", "movement": None,
                             "changes": [[1, 0, 0, 1], [1, 0, 2, 263]], "owners": []}]}
        self.assertIsNone(checker.consume(finish, 1))

    def test_bounded_mode_rejects_detached_stationary_identity_outside_shifted_envelope(self):
        lower, upper = (0, 0, 0), (1, 0, 1)
        initial = {"initial": [[0, 0, 0, 1], [0, 0, 1, 1]],
                   "initial_owners": [], "steps": []}
        checker = CaseChecker(contract(
            Port("out", "output", (0, 0, 0), "m", None, None),
            recurrence="bounded", boundary_envelope=(lower, upper)), initial)
        start = {"initial": initial["initial"], "initial_owners": [],
                 "steps": [{"tick": 0, "action": "extend", "movement": {
                     "sources": [[0, 0, 0]], "destinations": [[1, 0, 0]], "failure": None},
                     "changes": [[0, 0, 0, None], [1, 0, 0, 17]], "owners": []}]}
        self.assertIsNone(checker.consume(start, 0))
        finish = {"initial": [[0, 0, 1, 1], [1, 0, 0, 17]], "initial_owners": [],
                  "steps": [{"tick": 1, "action": "finish extension", "movement": None,
                             "changes": [[1, 0, 0, 1]], "owners": []}]}
        self.assertIn("outside translated boundary_envelope", checker.consume(finish, 1))

    def test_bounded_mode_requires_initial_identity_enclosure(self):
        initial = {"initial": [[0, 0, 0, 1], [2, 0, 0, 1]],
                   "initial_owners": [], "steps": []}
        with self.assertRaisesRegex(ContractError, "initial permanent identity"):
            CaseChecker(contract(
                Port("out", "output", (0, 0, 0), "m", None, None),
                recurrence="bounded", boundary_envelope=((0, 0, 0), (1, 0, 0))), initial)

    def test_bounded_contract_requires_valid_envelope(self):
        path = ROOT / "tests" / "bad_extension_contract.json"
        base = ('"version":1,"name":"bad","flyer":"x.flyer",'
                '"period_ticks":2,"advance":1,"ports":[{"name":"o",'
                '"role":"output","at":[0,0,0],"word":"m"}],')
        cases = [
            ("{" + base + '"recurrence":"bounded"}', "required object"),
            ("{" + base + '"recurrence":"bounded","boundary_envelope":{"min":[1,0,0],"max":[0,0,0]}}', "min must be <= max"),
            ("{" + base + '"recurrence":"bounded","boundary_envelope":{"min":[0,0,0],"max":[1,0,0],"extra":1}}', "unknown field"),
            ("{" + base + '"boundary_envelope":{"min":[0,0,0],"max":[1,0,0]}}', "only allowed"),
        ]
        try:
            for raw, message in cases:
                path.write_text(raw, encoding="utf-8")
                with self.subTest(message=message), self.assertRaisesRegex(ContractError, message):
                    load_contract(path)
        finally:
            path.unlink(missing_ok=True)

    def test_real_extension_trace_backend_on_bank_fixture(self):
        from fastflyer import Flyer
        from extension_contract import run_case, _driver_path

        try:
            driver = _driver_path()
        except ContractError:
            self.skipTest("build target/release/extension-trace to run integration test")
        source = ROOT / "flyers" / "bank" / "pl3" / "upright_pair.flyer"
        with tempfile.TemporaryDirectory(dir=ROOT / "target") as temp:
            fixture = Path(temp) / "upright_pair.flyer"
            Flyer.load(source).save(fixture)
            spec = Contract("upright-pair", fixture, 6, 1, 2, (
                Port("rear", "output", (0, 0, 0), "wwm", None, None),
                Port("front", "output", (1, 0, 0), "mww", None, None),
            ))
            result = run_case(spec, driver, None)
            owned_fixture = Path(temp) / "upright_pair_owned.flyer"
            owned = Flyer.load(source)
            owned.set_piston_blocks((0, 0, 0), [(1, 0, 0)])
            owned.save(owned_fixture)
            owned_spec = Contract("upright-pair-owned", owned_fixture, 6, 1, 1, (
                Port("rear", "output", (0, 0, 0), "wwm", None, None),
                Port("front", "output", (1, 0, 0), "mww", None, None),
            ))
            owner_result = run_case(owned_spec, driver, None)
        self.assertTrue(result["passed"], result["diagnostic"])
        self.assertEqual(result["whole_assembly_max_action"], 3)
        self.assertFalse(owner_result["passed"])
        self.assertIn("owner recurrence mismatch", owner_result["diagnostic"])

    def test_real_external_drive_backend_on_three_glue_mmmww_fixture(self):
        from extension_contract import _driver_path

        try:
            driver = _driver_path(external=True)
        except ContractError:
            self.skipTest("build target/release/extension-drive to run integration test")
        spec_path = ROOT / "flyers" / "WIP" / "experiments" / "extension_contract_20261011" / \
            "external_drive" / "contracts" / "mmmww.json"
        if not spec_path.is_file():
            self.skipTest("external_drive benchmark fixture is not present")
        spec = load_contract(spec_path)
        result = run_case(spec, driver, None)
        self.assertTrue(result["passed"], result["diagnostic"])
        self.assertEqual(result["ticks"], spec.period_ticks * spec.cycles)
        self.assertEqual(result["whole_assembly_max_action"], 3)
        self.assertEqual(result["input_max_action_loads"]["driver_low"], [3, 3, 3, None, None])

    def test_unknown_fields_and_malformed_contract_are_rejected(self):
        path = Path(__file__).with_name("bad_extension_contract.json")
        path.write_text('{"version":1,"name":"bad","flyer":"x.flyer",'
                        '"period_ticks":2,"advance":1,"ports":[],"silently_ignored":true}')
        try:
            with self.assertRaisesRegex(ContractError, "unknown field"):
                load_contract(path)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
