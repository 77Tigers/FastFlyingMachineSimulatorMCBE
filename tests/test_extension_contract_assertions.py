import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))

from extension_contract import (  # noqa: E402
    CaseChecker, Contract, ContractError, Port, PrescribedEvent, load_contract,
)
from extension_design import compile_design  # noqa: E402


class ExtensionContractAssertionTests(unittest.TestCase):
    def _contract_file(self, raw):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "contract.json"
        path.write_text(json.dumps(raw), encoding="utf-8")
        return path

    def _raw(self):
        return {
            "version": 1, "name": "assertions", "flyer": "x.flyer",
            "period_ticks": 4, "advance": 1,
            "ports": [
                {"name": "a", "role": "output", "at": [0, 0, 0], "word": "mw",
                 "provenance": ["supplied", None]},
                {"name": "b", "role": "output", "at": [0, 0, 1], "word": "mw",
                 "provenance": ["supplied", None]},
            ],
            "contacts": [{"name": "touch", "a": "a", "b": "b", "relation": "offset",
                          "offset": [0, 0, 1], "slots": [0]}],
        }

    def test_compiler_emits_assertions_and_standalone_contract_loads_them(self):
        design_path = PROJECT / "flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/rear_cap_design.json"
        raw = json.loads(design_path.read_text(encoding="utf-8"))
        result = compile_design(raw)
        contract = result["contract"]
        self.assertEqual(contract["ports"][0]["provenance"], raw["ports"][0]["provenance"])
        self.assertEqual(contract["contacts"], result["plan"]["contacts"])
        path = self._contract_file(contract)
        (path.parent / "prescribed.txt").write_text(result["prescribed_text"], encoding="utf-8")
        loaded = load_contract(path)
        self.assertEqual(loaded.ports[0].provenance, tuple(raw["ports"][0]["provenance"]))
        self.assertEqual(loaded.contacts[0].name, contract["contacts"][0]["name"])

    def test_legacy_contract_without_assertions_still_loads(self):
        raw = self._raw()
        raw.pop("contacts")
        for port in raw["ports"]:
            port.pop("provenance")
        contract = load_contract(self._contract_file(raw))
        self.assertEqual(contract.contacts, ())
        self.assertIsNone(contract.ports[0].provenance)

    def test_malformed_provenance_and_contacts_are_rejected(self):
        raw = self._raw()
        raw["ports"][0]["provenance"] = ["supplied", "internal"]
        with self.assertRaisesRegex(ContractError, "waits must be null"):
            load_contract(self._contract_file(raw))
        raw = self._raw()
        raw["ports"][1]["provenance"] = ["unknown", None]
        with self.assertRaisesRegex(ContractError, "internal or supplied"):
            load_contract(self._contract_file(raw))
        raw = self._raw()
        raw["ports"][0]["provenance"] = {"slot": "supplied"}
        with self.assertRaisesRegex(ContractError, "expected an array"):
            load_contract(self._contract_file(raw))
        raw = self._raw()
        raw["ports"][0]["provenance"][0] = {"source": "supplied"}
        with self.assertRaisesRegex(ContractError, "internal or supplied"):
            load_contract(self._contract_file(raw))
        raw = self._raw()
        raw["contacts"][0]["a"] = "missing"
        with self.assertRaisesRegex(ContractError, "declared ports"):
            load_contract(self._contract_file(raw))
        raw = self._raw()
        raw["contacts"][0]["slots"] = [2]
        with self.assertRaisesRegex(ContractError, "slot indices"):
            load_contract(self._contract_file(raw))
        raw = self._raw()
        raw["contacts"][0]["slots"] = [0, 0]
        with self.assertRaisesRegex(ContractError, "duplicate slot"):
            load_contract(self._contract_file(raw))

    def test_contact_uses_initial_identity_positions_and_allows_aliases(self):
        contact = {"name": "same", "a": "left", "b": "right", "relation": "same", "slots": [0]}
        contract = Contract("alias", Path("x.flyer"), 4, 1, 1,
                            (Port("left", "output", (0, 0, 0), "mw", None, None),
                             Port("right", "output", (0, 0, 0), "mw", None, None)),
                            contacts=())
        # Construct parsed contact through the JSON loader, then use the same identity twice.
        raw = self._raw()
        raw["ports"] = [{"name": "left", "role": "output", "at": [0, 0, 0], "word": "mw"},
                        {"name": "right", "role": "output", "at": [0, 0, 0], "word": "mw"}]
        raw["contacts"] = [contact]
        loaded = load_contract(self._contract_file(raw))
        trace = {"initial": [[0, 0, 0, 1]], "initial_owners": [], "steps": [
            {"tick": 0, "stage": "chunk", "action": None, "changes": [], "owners": []}]}
        checker = CaseChecker(loaded, trace)
        failure = checker.consume(trace, 0, defer_recurrence=True)
        self.assertIn("expected move +X", failure)
        self.assertEqual(checker.first_failure["stage"], "motion")
        self.assertEqual(checker.port_ids["left"], checker.port_ids["right"])

    def test_standalone_checker_rejects_wrong_contact_before_actions(self):
        raw = self._raw()
        raw["contacts"][0]["offset"] = [1, 0, 1]
        contract = load_contract(self._contract_file(raw))
        trace = {"initial": [[0, 0, 0, 1], [0, 0, 1, 1]], "initial_owners": [], "steps": [
            {"tick": 0, "stage": "chunk", "action": None, "changes": [], "owners": []}]}
        checker = CaseChecker(contract, trace)
        failure = checker.consume(trace, 0, defer_recurrence=True)
        self.assertIn("contact touch", failure)
        self.assertEqual(checker.first_failure["stage"], "contact")

    def test_standalone_checker_rejects_supplied_passenger_labeled_internal(self):
        ports = (Port("feed", "input", (0, 0, 0), "mw", None, None, ("supplied", None)),
                 Port("passenger", "output", (0, 0, 1), "mw", None, None, ("internal", None)))
        contract = Contract("passenger", Path("x.flyer"), 4, 1, 1, ports,
                            prescribed_script=Path("script.txt"), prescribed_order="before_natural",
                            prescribed=(PrescribedEvent(0, (0, 0, 0), 2),))
        initial = {"initial": [[0, 0, 0, 1], [0, 0, 1, 1]], "initial_owners": [], "steps": []}
        checker = CaseChecker(contract, initial)
        trace = {"initial": initial["initial"], "initial_owners": [], "steps": [
            {"tick": 0, "stage": "prescribed", "action": "prescribed move",
             "active_input": [0, 0, 0], "prescribed_move_id": 0,
             "movement": {"sources": [[0, 0, 0], [0, 0, 1]],
                          "destinations": [[1, 0, 0], [1, 0, 1]], "failure": None},
             "changes": [[0, 0, 0, None], [0, 0, 1, None],
                         [1, 0, 0, 17], [1, 0, 1, 17]], "owners": []},
            {"tick": 0, "stage": "chunk", "action": None, "changes": [], "owners": []}]}
        failure = checker.consume(trace, 0, defer_recurrence=True)
        self.assertIn("expected provenance internal, observed supplied", failure)
        self.assertEqual(checker.first_failure["port"], "passenger")


if __name__ == "__main__":
    unittest.main()
